from rest_framework import serializers

from hotel_app.models.servicio import Servicio


class ServicioSerializer(serializers.ModelSerializer):
    imagen = serializers.ImageField(
        write_only=True,
        required=False,
        allow_null=True,
    )
    imagen_url = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = Servicio
        fields = [
            'id',
            'nombre',
            'descripcion',
            'tipo_servicio',
            'precio_extra',
            'icono',
            'imagen',
            'imagen_url',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'imagen_url',
            'created_at',
            'updated_at',
        ]

    def get_imagen_url(self, obj):
        if not obj.imagen:
            return None

        request = self.context.get('request')
        image_url = obj.imagen.url
        return (
            request.build_absolute_uri(image_url)
            if request is not None
            else image_url
        )