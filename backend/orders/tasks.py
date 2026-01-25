from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from orders.models import Order



@shared_task
def send_order_confirmation_email(order_id):
    order = Order.objects.get(id=order_id)
    send_mail(
        subject=f'Order {order.id} confirmed',
        message=f'Your order {order.id} has been confirmed.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.user.email],
    )


@shared_task
def send_order_to_admin(order_id):
    order = Order.objects.get(id=order_id)

    items = order.items.select_related('product_info', 'product_info__product')

    lines = []
    for item in items:
        lines.append(
            f"{item.product_info.product.name} - "
            f"{item.quantity} шт х {item.product_info.price}"
        )

    contact = order.contact
    apartment = (
        contact.apartment
        if getattr(contact, 'apartment', None)
        else "not specified"
    )
    body = f"""
        Новый заказ №{order.id}

        Клиент: {order.user.email}

        Состав заказа:
        {chr(10).join(lines)}

        Итого: {order.total_price}

        Контактные данные:
        Телефон: {contact.phone},
        Город: {contact.city},
        Улица: {contact.street},
        Дом: {contact.house},
        Квартира: {apartment}
    """

    send_mail(
        subject=f"Накладная по заказу №{order.id}",
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.ADMIN_EMAIL],
    )

