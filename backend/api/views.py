from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from importer.services import import_products_from_yaml
from products.models import Product
from products.serializers import ProductSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from orders.models import Order, OrderItem
from orders.serializers import OrderSerializer, OrderItemSerializer, OrderConfirmSerializer
from orders.tasks import send_order_confirmation_email
from accounts.serializers import RegisterSerializer


# Create your views here.


class ImportProductsView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        file_path = request.data.get('file_path')

        if not file_path:
            return Response(
                {'error': 'file_path is required'}, 
                status=400
            )
        
        import_products_from_yaml(file_path)
        return Response({'status': 'import started'})
        

class ProductListView(ListAPIView):
    serializer_class = ProductSerializer
    
    def get_queryset(self):
        qs = Product.objects.all()

        shop_id = self.request.query_params.get('shop')
        category_id = self.request.query_params.get('category')

        if shop_id:
            qs = qs.filter(product_infos__shop_id=shop_id)

        if category_id:
            qs = qs.filter(category_id=category_id)

        return qs.distinct()
    

class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, _ = Order.objects.get_or_create(
            user=request.user,
            status='cart'
        )
        serializer = OrderSerializer(cart)
        return Response(serializer.data)
    
    def post(self, request):
        cart, _ = Order.objects.get_or_create(
            user=request.user,
            status='cart'
        )

        serializer = OrderItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item, created = OrderItem.objects.get_or_create(
            order=cart,
            product_info=serializer.validated_data['product_info'],
            defaults={
                'quantity': serializer.validated_data['quantity']
            }
        )
        if not created:
            item.quantity += serializer.validated_data['quantity']
            item.save()

        return Response({'status': 'item added'})


class OrderConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = OrderConfirmSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        try:
            order = Order.objects.filter(
                user=request.user,
                status='new'
            ).order_by('-created_at').first()
            
            order.status = 'confirmed'
            order.save()

        except:
            return Response(
                {'error': 'No new orders found'}, 
                status=400
            )
            
        try:
            send_order_confirmation_email.delay(order.id)
        except Exception as e:
            print('Celery error', e)

        return Response({'status': 'order confirmed'})


class OrderListView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).exclude(status='cart')
    

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        return Response(
            {
                'status': 'user created',
                'username': user.username
            },
            status=status.HTTP_201_CREATED
        )