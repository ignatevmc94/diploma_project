from rest_framework import serializers

from contacts.serializers import ContactSerializer
from contacts.models import Contact
from .models import Order, OrderItem
from products.models import ProductInfo



class OrderItemSerializer(serializers.ModelSerializer):
    product_info = serializers.PrimaryKeyRelatedField(
        queryset=ProductInfo.objects.all(),
        )

    class Meta:
        model = OrderItem
        fields = ['id', 'product_info', 'quantity']


class OrderItemDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source='product_info.product.name',
        read_only=True
    )
    shop = serializers.CharField(
        source='product_info.shop.name',
        read_only=True
    )
    price = serializers.DecimalField(
        source='product_info.price',
        max_digits=10, 
        decimal_places=2,
        read_only=True
    )
    status = serializers.CharField(read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'shop', 'product_name', 'quantity', 'price', 'total_price', 'status']

    def get_total_price(self, instance):
        return instance.product_info.price * instance.quantity


class OrderListSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )

    class Meta:
        model = Order
        fields = ['id', 'status', 'items', 'total_price', 'created_at']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    total_price = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )


    class Meta:
        model = Order
        fields = ['id', 'status', 'items', 'total_price', 'created_at']


class OrderConfirmSerializer(serializers.Serializer):
    contact_id = serializers.IntegerField(required=False)
    contact = ContactSerializer(required=False)

    def validate(self, data):
        
        if ("contact_id" in data) == ("contact" in data):
            raise serializers.ValidationError(
                "Only contact_id OR contact needed."
            )

        if not data.get('contact_id') and not data.get('contact'):
            raise serializers.ValidationError(
                'Contact_id or contact must be provided.'
            )

        return data
    

class SupplierOrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source='product_info.product.name',
        read_only=True
    )
    price = serializers.DecimalField(
        source='product_info.price',
        max_digits=10, 
        decimal_places=2,
        read_only=True
    )
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product_name', 'quantity', 'price', 'total_price']

    def get_total_price(self, instance):
        return instance.product_info.price * instance.quantity


class SupplierOrderDetailSerializer(serializers.ModelSerializer):
    customer = serializers.CharField(
        source='user.username',
        read_only=True
    )
    customer_email = serializers.EmailField(
        source='user.email',
        read_only=True
    )

    items = serializers.SerializerMethodField()
    contact = ContactSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()
    supplier_status = serializers.SerializerMethodField()

    class Meta:
        model = Order
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
        request = self.context.get("request")
        supplier_shop_name = request.user.username

        qs = instance.items.filter(
            product_info__shop__name=supplier_shop_name
        )

        if not qs.exists():
            return None
        return "done" if not qs.exclude(status="done").exists() else "confirmed"
    
    def get_items(self, instance):
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
    is_accepting_orders = serializers.BooleanField()


class SupplierOrderStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=["confirmed", "done"])

