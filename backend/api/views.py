from django.shortcuts import get_object_or_404

from django.contrib.auth.forms import PasswordResetForm

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from contacts.models import Contact
from contacts.serializers import ContactSerializer

from importer.services import import_products_from_yaml

from orders.models import Order, OrderItem
from orders.serializers import (
    OrderConfirmSerializer,
    OrderItemSerializer,
    OrderListSerializer,
    OrderSerializer,
    SupplierAcceptionSerializer,
    SupplierOrderDetailSerializer,
    SupplierOrderStatusSerializer,
)
from orders.tasks import send_order_confirmation_email, send_order_to_admin

from products.models import Product
from products.serializers import ProductDetailSerializer, ProductSerializer

from shops.models import Shop

from accounts.serializers import LoginSerializer, RegisterSerializer

from .permissions import IsSupplier


# ----------------------------
# Импорт товаров (только поставщик)
# ----------------------------
class ImportProductsView(APIView):
    permission_classes = [IsAuthenticated, IsSupplier]

    def post(self, request):
        file_path = request.data.get("file_path")

        if not file_path:
            return Response({"error": "file_path is required"}, status=400)

        try:
            result = import_products_from_yaml(
                file_path=file_path,
                user=request.user,
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

        return Response(result, status=200)


# ----------------------------
# Товары (публичный список)
# ----------------------------
class ProductListView(ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = Product.objects.all()

        shop_id = self.request.query_params.get("shop")
        category_id = self.request.query_params.get("category")

        if shop_id:
            qs = qs.filter(product_infos__shop_id=shop_id)

        if category_id:
            qs = qs.filter(category_id=category_id)

        return qs.distinct()


# ----------------------------
# Товар (публичные детали)
# ----------------------------
class ProductDetailView(RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]


# ----------------------------
# Корзина пользователя
# ----------------------------
class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Order.objects.get_or_create(user=request.user, status="cart")
        serializer = OrderListSerializer(cart)
        return Response(serializer.data)

    def post(self, request):
        cart, _ = Order.objects.get_or_create(user=request.user, status="cart")

        serializer = OrderItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item, created = OrderItem.objects.get_or_create(
            order=cart,
            product_info=serializer.validated_data["product_info"],
            defaults={"quantity": serializer.validated_data["quantity"],
                      "status": "cart"
                      },
        )

        supplier_shop = item.product_info.shop

        if not supplier_shop.is_accepting_orders:
            return Response(
                {"error": "This shop is not accepting orders at the moment"},
                status=400,
            )

        if not created:
            item.quantity += serializer.validated_data["quantity"]
            item.save()

        return Response({"status": "item added"})


# ----------------------------
# Удаление позиции из корзины
# ----------------------------
class CartItemDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        try:
            item = OrderItem.objects.get(
                id=item_id,
                order__user=request.user,
                order__status="cart",
            )
        except OrderItem.DoesNotExist:
            return Response({"error": "Item not found in cart"}, status=404)

        item.delete()
        return Response({"status": "item deleted"})


# ----------------------------
# Создать заказ (cart -> new)
# ----------------------------
class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        cart = Order.objects.filter(user=request.user, status="cart").first()

        if not cart or not cart.items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        cart.status = "new"
        cart.save()

        return Response({"status": "Order created"})


# ----------------------------
# Подтвердить заказ (new -> confirmed)
# ----------------------------
class OrderConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        data = serializer.validated_data

        order = (
            Order.objects.filter(user=request.user, status="new")
            .order_by("-created_at")
            .first()
        )

        if not order:
            return Response({"error": "No new orders found"}, status=400)

        # Контакт: либо существующий, либо новый
        if "contact_id" in data:
            contact = get_object_or_404(Contact, id=data["contact_id"], user=user)
        else:
            contact_serializer = ContactSerializer(data=data["contact"])
            contact_serializer.is_valid(raise_exception=True)
            contact = contact_serializer.save(user=user)

        # Проверяем, что все магазины принимают заказы
        items = order.items.select_related("product_info__shop")
        for item in items:
            if not item.product_info.shop.is_accepting_orders:
                return Response(
                    {"error": "One of the shops is not accepting orders right now"},
                    status=400,
                )

        order.contact = contact
        order.status = "confirmed"
        order.save()

        # Подтверждаем позиции
        order.items.update(status="confirmed")

        # Уведомления
        try:
            send_order_confirmation_email.delay(order.id)
            send_order_to_admin.delay(order.id)
        except Exception as e:
            print("Celery error:", e)

        return Response({"status": "order confirmed"})


# ----------------------------
# Заказы пользователя
# ----------------------------
class OrderListView(ListAPIView):
    serializer_class = OrderListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).exclude(status="cart")


class OrderView(RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user, id=self.kwargs["pk"])
            .exclude(status="cart")
        )


# ----------------------------
# Регистрация / логин
# ----------------------------
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        return Response(
            {"status": "user created", "username": user.username},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)

        return Response({"token": token.key})


# ----------------------------
# Сброс пароля
# ----------------------------
class PasswordResetAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"error": "Email is required"}, status=400)

        form = PasswordResetForm(data={"email": email})

        if form.is_valid():
            form.save(
                request=request,
                use_https=False,
                email_template_name="registration/password_reset_email.html",
            )
            return Response({"status": "password reset email sent"})

        return Response({"error": "Invalid email"}, status=400)


# ----------------------------
# Контакты (адреса доставки)
# ----------------------------
class ContactView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        contacts = Contact.objects.filter(user=request.user)
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ContactSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        Contact.objects.create(user=request.user, **serializer.validated_data)
        return Response({"status": "contact created"}, status=201)


class ContactDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        contact = Contact.objects.filter(id=pk, user=request.user).first()

        if not contact:
            return Response({"error": "Contact not found"}, status=404)

        serializer = ContactSerializer(contact, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"status": "contact updated"})

    def delete(self, request, pk):
        contact = Contact.objects.filter(id=pk, user=request.user).first()

        if not contact:
            return Response({"error": "Contact not found"}, status=404)

        contact.delete()
        return Response({"status": "contact deleted"})


# ----------------------------
# Заказы поставщика (только его позиции)
# ----------------------------
class SupplierOrderListView(ListAPIView):
    serializer_class = SupplierOrderDetailSerializer
    permission_classes = [IsAuthenticated, IsSupplier]

    def get_queryset(self):
        # ВАЖНО: фильтруем по shop.user, а не по имени магазина
        return (
            Order.objects.filter(items__product_info__shop__user=self.request.user)
            .exclude(status="cart")
            .select_related("user", "contact")
            .prefetch_related("items__product_info__product", "items__product_info__shop")
            .distinct()
            .order_by("-created_at")
        )


# ----------------------------
# Поставщик включает/выключает прием заказов
# ----------------------------
class SupplierAcceptionView(APIView):
    permission_classes = [IsAuthenticated, IsSupplier]

    def post(self, request):
        serializer = SupplierAcceptionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Берём магазин, который принадлежит пользователю
        shop = Shop.objects.filter(user=request.user).first()

        if not shop:
            return Response({"error": "Shop not found"}, status=404)

        shop.is_accepting_orders = serializer.validated_data["is_accepting_orders"]
        shop.save()

        return Response(
            {
                "is_accepting_orders": shop.is_accepting_orders,
                "message": (
                    "supplier is now accepting orders"
                    if shop.is_accepting_orders
                    else "supplier is not accepting orders temporarily"
                ),
            }
        )


# ----------------------------
# Поставщик меняет статус своих позиций в заказе
# ----------------------------
class SupplierOrderStatusView(APIView):
    permission_classes = [IsAuthenticated, IsSupplier]

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk")

        # Берём позиции заказа только текущего поставщика
        qs = OrderItem.objects.filter(
            order_id=pk,
            product_info__shop__user=request.user,
        ).exclude(order__status="cart")

        if not qs.exists():
            return Response({"error": "Order not found"}, status=404)

        supplier_status = "done" if not qs.exclude(status="done").exists() else "confirmed"

        return Response({"order_id": pk, "supplier_status": supplier_status})

    def post(self, request, *args, **kwargs):
        pk = kwargs.get("pk")

        serializer = SupplierOrderStatusSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data["status"]

        # Меняем статус всех позиций поставщика в этом заказе
        qs = OrderItem.objects.filter(
            order_id=pk,
            product_info__shop__user=request.user,
        ).exclude(order__status="cart")

        if not qs.exists():
            return Response({"error": "Order not found"}, status=404)

        updated_count = qs.update(status=new_status)

        # Если все позиции done -> закрываем весь заказ
        order = Order.objects.filter(id=pk).exclude(status="cart").first()
        if order and not order.items.exclude(status="done").exists():
            order.status = "done"
            order.save()

        return Response(
            {
                "order_id": pk,
                "supplier_status": new_status,
                "updated_items": updated_count,
                "message": "Supplier items status updated",
            }
        )
