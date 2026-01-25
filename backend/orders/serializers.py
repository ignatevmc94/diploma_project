from rest_framework import serializers

from contacts.serializers import ContactSerializer
from contacts.models import Contact
from .models import Order, OrderItem
from products.models import ProductInfo


class ProductInfoSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name')
    shop_name = serializers.CharField(source='shop.name')

    class Meta:
        model = ProductInfo
        fields = ['id', 'product_name', 'shop_name', 'quantity', 'price', 'price_rrc']



class OrderItemSerializer(serializers.ModelSerializer):
    product_info = ProductInfoSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product_info']


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
    

class SupplierOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        read_only=True
    )

    class Meta:
        model = Order
        fields = ['id', 'status', 'items', 'total_price', 'created_at']


class SupplierAcceptionSerializer(serializers.Serializer):
    is_accepting_orders = serializers.BooleanField()