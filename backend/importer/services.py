import yaml

from shops.models import Shop, Category
from products.models import Product, ProductInfo, Parameter, ProductParameter


def import_products_from_yaml(file_path, user):
    with open(file_path, encoding='utf-8') as f:
        data = yaml.safe_load(f)

    yaml_shop_name = data.get("shop")
    if not yaml_shop_name:
        raise ValueError("YAML must contain 'shop' field")
    
    shop = Shop.objects.filter(user=user).first()

    if not shop:
        if Shop.objects.filter(name=yaml_shop_name).exclude(user=user).exists():
            raise ValueError("Shop with this name already exists and belongs to another user")
        
        shop = Shop.objects.create(
            name=yaml_shop_name,
            user=user
        )

    if shop.name != yaml_shop_name:
        raise ValueError(
            f"You can import only your shop '{shop.name}', not '{yaml_shop_name}'"
        )

    categories_map = {}
    for category_data in data['categories']:
        category, _ = Category.objects.get_or_create(
            name=category_data['name']
        )
        category.shops.add(shop)
        categories_map[category_data['id']] = category

    for item in data['goods']:
        category = categories_map.get(item['category'])
        if not category:
            continue

        product, _ = Product.objects.get_or_create(
            name=item['name'],
            category=category
        )

        product_info, _ = ProductInfo.objects.update_or_create(
            product=product,
            shop=shop,
            defaults={
                'price': item['price_rrc'],
                'price_rrc': item['price_rrc'],
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
                defaults={'value': str(param_value)}
            )
    return {
        "status": "import completed",
        "shop": shop.name,
    }
