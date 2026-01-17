import yaml

from shops.models import Shop, Category
from products.models import Product, ProductInfo, Parameter, ProductParameter


def impor_products_from_yaml(file_path: str):
    with open(file_path, encoding='utf-8') as f:
        data = yaml.safe_load(f)

    shop, _ = Shop.objects.get_or_create(
        name=data['shop'],
        defaults={'is_active': True}
    )

    for category_data in data['categories']:
        category, _ = Category.objects.get_or_create(
            name=category_data['name'],
        )
        category.shops.add(shop)

        for item in category_data['items']:
            product, _ = Product.objects.get_or_create(
                name=item['name'],
                category=category
            )

            product_info, _ = ProductInfo.objects.update_or_create(
                product=product,
                shop=shop,
                defaults={
                    'price': item['price'],
                    'quantity': item['quantity']
                }
            )

            for param_name, param_value in item.get('parameters', {}).items():
                parameter, _ = Parameter.objects.get_or_create(
                    name=param_name
                )
                ProductParameter.objects.update_or_create(
                    product_info=product_info,
                    parameter=parameter,
                    defaults={'value': param_value}
                )




