from rest_framework import serializers
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

