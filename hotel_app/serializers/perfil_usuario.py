from django.contrib.auth.models import User
from rest_framework import serializers

from hotel_app.models import PerfilUsuario


class RegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    class Meta:
        model = User

        fields = [
            'username',
            'email',
            'password',
        ]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )

        PerfilUsuario.objects.create(
            user=user,
        )

        return user


class PerfilUsuarioSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source='user.username',
        read_only=True,
    )

    email = serializers.EmailField(
        source='user.email',
        read_only=True,
    )

    foto = serializers.ImageField(
        source='foto_url',
        write_only=True,
        required=False,
        allow_null=True,
    )

    foto_url = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = PerfilUsuario

        fields = [
            'id',
            'user',
            'username',
            'email',
            'rol',
            'telefono',
            'foto',
            'foto_url',
            'estado',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'user',
            'username',
            'email',
            'foto_url',
            'created_at',
            'updated_at',
        ]

    def get_foto_url(self, obj):
        if not obj.foto_url:
            return None

        try:
            photo_url = obj.foto_url.url
        except ValueError:
            return None

        request = self.context.get('request')

        if request is not None:
            return request.build_absolute_uri(photo_url)

        return photo_url


class PerfilActualSerializer(PerfilUsuarioSerializer):
    class Meta(PerfilUsuarioSerializer.Meta):
        read_only_fields = [
            *PerfilUsuarioSerializer.Meta.read_only_fields,
            'rol',
            'estado',
        ]