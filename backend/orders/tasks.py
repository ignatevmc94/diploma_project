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