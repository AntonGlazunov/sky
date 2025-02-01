from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users_api.models import User


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'pk']
        extra_kwargs = {'password': {'write_only': True}, 'pk': {'read_only': True}}


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Добавление пользовательских полей в токен
        token['username'] = user.username
        user.save()

        return token
