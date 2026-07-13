from django.db import transaction
from rest_framework import serializers

from hotel_app.models.imagen_habitacion import ImagenHabitacion


class ImagenHabitacionSerializer(serializers.ModelSerializer):
    imagen = serializers.ImageField(
        source='imagen_url',
        write_only=True,
        required=True,
    )

    imagen_url = serializers.SerializerMethodField(
        read_only=True,
    )

    habitacion_numero = serializers.CharField(
        source='habitacion.numero',
        read_only=True,
    )

    class Meta:
        model = ImagenHabitacion

        fields = [
            'id',
            'habitacion',
            'habitacion_numero',
            'imagen',
            'imagen_url',
            'titulo',
            'descripcion',
            'orden',
            'es_principal',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'habitacion_numero',
            'imagen_url',
            'created_at',
            'updated_at',
        ]

    def get_imagen_url(self, obj):
        if not obj.imagen_url:
            return None

        try:
            image_url = obj.imagen_url.url
        except ValueError:
            return None

        request = self.context.get('request')

        if request is not None:
            return request.build_absolute_uri(image_url)

        return image_url

    def validate_orden(self, value):
        if value < 0:
            raise serializers.ValidationError(
                'El orden no puede ser negativo.'
            )

        return value

    @transaction.atomic
    def create(self, validated_data):
        imagen = super().create(validated_data)

        if imagen.es_principal:
            ImagenHabitacion.objects.filter(
                habitacion=imagen.habitacion,
                es_principal=True,
            ).exclude(
                id=imagen.id,
            ).update(
                es_principal=False,
            )

        return imagen

    @transaction.atomic
    def update(self, instance, validated_data):
        imagen = super().update(
            instance,
            validated_data,
        )

        if imagen.es_principal:
            ImagenHabitacion.objects.filter(
                habitacion=imagen.habitacion,
                es_principal=True,
            ).exclude(
                id=imagen.id,
            ).update(
                es_principal=False,
            )

        return imagen