from rest_framework import serializers
from .models import Product, ProductInfo, ProductParameter, Parameter, Category


class CategorySerializer(serializers.ModelSerializer):
    # сериализатор для категории (отдаём только имя)
    class Meta:
        model = Category
        fields = ['name']


class ParameterSerializer(serializers.ModelSerializer):
    # сериализатор для параметра товара (например: "цвет", "память")
    class Meta:
        model = Parameter
        fields = ['name']


class ProductParameterSerializer(serializers.ModelSerializer):
    # сериализатор связки "параметр + значение" для товара
    parameter = ParameterSerializer()

    class Meta:
        model = ProductParameter
        fields = ['parameter', 'value']


class ProductInfoSerializer(serializers.ModelSerializer):
    # сериализатор наличия товара в конкретном магазине (цена/остаток/параметры)
    parameters = ProductParameterSerializer(
        many=True
    )
    # shop выводится строкой через __str__ модели Shop
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
    # сериализатор списка товаров (категория + предложения по магазинам)
    category = CategorySerializer()
    product_infos = ProductInfoSerializer(many=True)
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'product_infos', 'image']


class ProductDetailSerializer(serializers.ModelSerializer):
    # сериализатор детальной информации по товару
    # категория выводится строкой через __str__ модели Category
    category = serializers.StringRelatedField()
    product_infos = ProductInfoSerializer(
        many=True
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'product_infos']

