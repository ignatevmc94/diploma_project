from django.contrib.auth import get_user_model
from rest_framework import serializers
from contacts.models import Contact


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        user.save()

        Contact.objects.create(
            user=user,
            city='',
            street='',
            house='',
            apartment='',
            phone=''
        )

        return user
    
