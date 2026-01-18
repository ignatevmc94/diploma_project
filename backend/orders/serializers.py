from rest_framework import serializers

from contacts.models import Contact
from .models import Order, OrderItem
from products.models import ProductInfo


class OrderItemSerializer(serializers.ModelSerializer):
    product_info = serializers.PrimaryKeyRelatedField(
        queryset=ProductInfo.objects.all()
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'product_info', 'quantity']

    

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
    contact_id = serializers.IntegerField()

    def validate_contact_id(self, value):
        user = self.context['request'].user
        
        if not Contact.objects.filter(id=value, user=user).exists():
            raise serializers.ValidationError("Contact not found")
        
        return value
    
