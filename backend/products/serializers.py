from rest_framework import serializers
from .models import Product, ProductInfo, ProductParameter, Parameter, Category



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']


class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ['name']


class ProductParameterSerializer(serializers.ModelSerializer):
    parameter = ParameterSerializer()

    class Meta:
        model = ProductParameter
        fields = ['parameter', 'value']


class ProductInfoSerializer(serializers.ModelSerializer):
    parameters = ProductParameterSerializer(
        many=True
    )
    shop = serializers.StringRelatedField()

    class Meta:
        model = ProductInfo
        fields = [
            'id',
            'shop',
            'price',
            'quantity',
            'parameters',
        ]


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    product_infos = ProductInfoSerializer(many=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'product_infos']


class ProductDetailSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()
    product_infos = ProductInfoSerializer(
        many=True
        )

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'product_infos']