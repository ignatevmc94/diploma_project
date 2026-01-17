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
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'status', 'items']


class OrderConfirmSerializer(serializers.Serializer):
    contact_id = serializers.IntegerField()

    def validate_contact_id(self, value):
        user = self.context['request'].user

        if not Contact.objects.filter(id=value, user=user).exists():
            raise serializers.ValidationError("Contact not found")
        
        return value
    
