from django.contrib.auth import get_user_model, authenticate
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
    

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False)
    email = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        email = attrs.get('email')
        password = attrs.get('password')
    
        if not password:
            raise serializers.ValidationError("Password is required")
        
        if not username and not email:
            raise serializers.ValidationError(
                "Provide either username or email"
            )

        user = None

        if email:
            try:
                user_obj = User.objects.get(email=email)
                user = authenticate(
                    username=user_obj.get_username(),
                    password=password
                )
            except User.DoesNotExist:
                pass
        
        if not user and username:
            try:
                user_obj = User.objects.get(username=username)
                user = authenticate(
                    username=user_obj.get_username(),
                    password=password
                )
            except User.DoesNotExist:
                pass

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        attrs['user'] = user
        return attrs
