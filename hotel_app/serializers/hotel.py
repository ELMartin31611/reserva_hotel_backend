from rest_framework import serializers

from hotel_app.models.hotel import Hotel


class HotelSerializer(serializers.ModelSerializer):
    logo = serializers.ImageField(
        write_only=True,
        required=False,
        allow_null=True,
    )

    logo_url = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = Hotel

        fields = [
            'id',
            'nombre',
            'ruc',
            'telefono',
            'email',
            'descripcion',
            'categoria_estrellas',
            'sitio_web',
            'logo',
            'logo_url',
            'estado',
            'hora_check_in',
            'hora_check_out',
            'permite_mascotas',
            'edad_minima_reserva',
            'politica_cancelacion',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'logo_url',
            'created_at',
            'updated_at',
        ]

        extra_kwargs = {
            'sitio_web': {
                'required': False,
                'allow_blank': True,
            },
        }

    def validate(self, attrs):
        if self.instance is None and not attrs.get('logo'):
            raise serializers.ValidationError({
                'logo': (
                    'Debes seleccionar una imagen para el logo '
                    'del hotel.'
                ),
            })

        return attrs

    def get_logo_url(self, obj):
        if obj.logo:
            try:
                image_url = obj.logo.url
            except ValueError:
                image_url = None

            if image_url:
                request = self.context.get('request')

                if request is not None:
                    return request.build_absolute_uri(image_url)

                return image_url

        return obj.logo_url or None