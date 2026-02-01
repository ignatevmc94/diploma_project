from celery import shared_task
from .models import Product


@shared_task
def generate_product_thumbnails(product_id):
    product = Product.objects.filter(id=product_id).first()
    if not product or not product.image:
        return

    product.image.get_thumbnail({'size': (300, 300), 'crop': True})

    