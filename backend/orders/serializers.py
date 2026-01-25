from rest_framework import serializers
from contacts.serializers import ContactSerializer
from .models import Order, OrderItem
from products.models import ProductInfo


class OrderItemSerializer(serializers.ModelSerializer):
    # принимает id ProductInfo при добавлении товара в корзину
    product_info = serializers.PrimaryKeyRelatedField(
        queryset=ProductInfo.objects.all(),
    )

    class Meta:
        model = OrderItem
        # минимальный набор полей для создания позиции
        fields = ['id', 'product_info', 'quantity']


class OrderItemDetailSerializer(serializers.ModelSerializer):
    # название товара
    product_name = serializers.CharField(
        source='product_info.product.name',
        read_only=True
    )
    # название магазина
    shop = serializers.CharField(
        source='product_info.shop.name',
        read_only=True
    )
    # цена товара в магазине
    price = serializers.DecimalField(
        source='product_info.price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    # статус позиции (confirmed/done)
    status = serializers.CharField(read_only=True)
    # сумма по позиции (price * quantity)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        # подробная выдача позиции заказа
        fields = ['id', 'shop', 'product_name', 'quantity', 'price', 'total_price', 'status']

    def get_total_price(self, instance):
        return instance.product_info.price * instance.quantity


class OrderListSerializer(serializers.ModelSerializer):
    # позиции заказа (для списка заказов)
    items = OrderItemSerializer(many=True, read_only=True)
    # общая сумма заказа
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Order
        # выдача заказа в списке
        fields = ['id', 'status', 'items', 'total_price', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    # позиции заказа (для деталей заказа)
    items = OrderItemSerializer(many=True, read_only=True)

    # общая сумма заказа
    total_price = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Order
        # выдача деталей заказа
        fields = ['id', 'status', 'items', 'total_price', 'created_at']


class OrderConfirmSerializer(serializers.Serializer):
    # можно передать либо id контакта
    contact_id = serializers.IntegerField(required=False)
    # либо новый контакт объектом
    contact = ContactSerializer(required=False)

    def validate(self, data):
        # нельзя передавать одновременно contact_id и contact
        if ("contact_id" in data) == ("contact" in data):
            raise serializers.ValidationError(
                "Only contact_id OR contact needed."
            )

        # обязательно должно быть что-то одно
        if not data.get('contact_id') and not data.get('contact'):
            raise serializers.ValidationError(
                'Contact_id or contact must be provided.'
            )

        return data


class SupplierOrderItemSerializer(serializers.ModelSerializer):
    # название товара для поставщика
    product_name = serializers.CharField(
        source='product_info.product.name',
        read_only=True
    )
    # цена товара
    price = serializers.DecimalField(
        source='product_info.price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    # сумма по позиции
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        # выдача позиции поставщику
        fields = ['id', 'product_name', 'quantity', 'price', 'total_price']

    def get_total_price(self, instance):
        return instance.product_info.price * instance.quantity


class SupplierOrderDetailSerializer(serializers.ModelSerializer):
    # покупатель (username)
    customer = serializers.CharField(
        source='user.username',
        read_only=True
    )
    # email покупателя
    customer_email = serializers.EmailField(
        source='user.email',
        read_only=True
    )

    # позиции заказа только этого поставщика
    items = serializers.SerializerMethodField()
    # контакт доставки
    contact = ContactSerializer(read_only=True)
    # сумма заказа только по товарам поставщика
    total_price = serializers.SerializerMethodField()
    # статус заказа с точки зрения поставщика
    supplier_status = serializers.SerializerMethodField()

    class Meta:
        model = Order
        # выдача заказа поставщику
        fields = [
            'id',
            'supplier_status',
            'customer',
            'customer_email',
            'items',
            'contact',
            'total_price',
            'created_at'
        ]

    def get_supplier_status(self, instance):
        # определяем статус по позициям текущего поставщика
        request = self.context.get("request")
        supplier_shop_name = request.user.username

        qs = instance.items.filter(
            product_info__shop__name=supplier_shop_name
        )

        if not qs.exists():
            return None
        return "done" if not qs.exclude(status="done").exists() else "confirmed"

    def get_items(self, instance):
        # отдаём только позиции текущего поставщика
        request = self.context.get("request")
        if not request:
            return []

        supplier_shop_name = request.user.username

        qs = instance.items.filter(
            product_info__shop__name=supplier_shop_name
        ).select_related(
            "product_info__product",
            "product_info__shop",
        )

        return OrderItemDetailSerializer(qs, many=True).data

    def get_total_price(self, instance):
        # считаем сумму только по товарам текущего поставщика
        request = self.context.get("request")
        if not request:
            return 0

        supplier_shop_name = request.user.username

        total = 0
        qs = instance.items.filter(
            product_info__shop__name=supplier_shop_name
        ).select_related("product_info")

        for item in qs:
            total += item.product_info.price * item.quantity

        return total


class SupplierAcceptionSerializer(serializers.Serializer):
    # включает/выключает прием заказов магазином
    is_accepting_orders = serializers.BooleanField()


class SupplierOrderStatusSerializer(serializers.Serializer):
    # статус, который поставщик может установить
    status = serializers.ChoiceField(choices=["confirmed", "done"])

