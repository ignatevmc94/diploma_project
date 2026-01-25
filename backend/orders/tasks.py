from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from orders.models import Order


@shared_task
def send_order_confirmation_email(order_id):
    # задача Celery: отправить письмо покупателю о подтверждении заказа
    order = Order.objects.get(id=order_id)
    send_mail(
        # тема письма
        subject=f'Order {order.id} confirmed',
        # текст письма
        message=f'Your order {order.id} has been confirmed.',
        # email отправителя (из настроек Django)
        from_email=settings.DEFAULT_FROM_EMAIL,
        # получатель = email пользователя заказа
        recipient_list=[order.user.email],
    )


@shared_task
def send_order_to_admin(order_id):
    # задача Celery: отправить админу накладную/детали заказа
    order = Order.objects.get(id=order_id)

    # вытягиваем позиции заказа вместе с ProductInfo и Product
    items = order.items.select_related('product_info', 'product_info__product')

    # формируем список строк с товарами (название + количество + цена)
    lines = []
    for item in items:
        lines.append(
            f"{item.product_info.product.name} - "
            f"{item.quantity} шт х {item.product_info.price}"
        )

    # берём контакт доставки
    contact = order.contact

    # квартира может быть пустой → подставляем "not specified"
    apartment = (
        contact.apartment
        if getattr(contact, 'apartment', None)
        else "not specified"
    )

    # тело письма админу (состав заказа + контакты)
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
        # тема письма
        subject=f"Накладная по заказу №{order.id}",
        # текст письма
        message=body,
        # email отправителя
        from_email=settings.DEFAULT_FROM_EMAIL,
        # получатель = админская почта из settings
        recipient_list=[settings.ADMIN_EMAIL],
    )

