from rest_framework import serializers
from .models import Product, ProductInfo, ProductParameter, Parameter


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
        source='productparameter_set',
        many=True
    )

    class Meta:
        model = ProductInfo
        fields = [
            'id',
            'model',
            'price',
            'price_rrc',
            'quantity',
            'parameters',
        ]


class ProductSerializer(serializers.ModelSerializer):
    product_infos = ProductInfoSerializer(
        source='productinfo_set',
        many=True
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'product_infos']