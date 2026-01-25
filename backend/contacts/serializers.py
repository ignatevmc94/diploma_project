from rest_framework import serializers
from .models import Contact


class ContactSerializer(serializers.ModelSerializer):
    """Сериализатор адреса доставки пользователя."""

    class Meta:
        model = Contact
        # Поля адреса, которые отдаём/принимаем через API
        fields = [
            "id",
            "phone",
            "city",
            "street",
            "house",
            "apartment",
        ]