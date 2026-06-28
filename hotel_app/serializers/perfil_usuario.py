from django.contrib.auth.models import User
from rest_framework import serializers

from hotel_app.models import PerfilUsuario


class RegistroSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password'
        ]

    def create(self, validated_data):

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        PerfilUsuario.objects.create(
            user=user
        )

        return user


class PerfilUsuarioSerializer(serializers.ModelSerializer):

    username = serializers.CharField(
        source='user.username',
        read_only=True
    )

    email = serializers.EmailField(
        source='user.email',
        read_only=True
    )

    class Meta:
        model = PerfilUsuario
        fields = '__all__'