from rest_framework import serializers

from hotel_app.models.hotel import Hotel


class HotelSerializer(serializers.ModelSerializer):
    """
    Serializer para consultar y administrar hoteles.

    El logo se recibe como archivo multipart mediante el campo
    `logo`. La respuesta devuelve la dirección pública mediante
    `logo_url`.
    """

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
        """
        Obliga a seleccionar un logo cuando se crea un hotel.

        Al editarlo se permite conservar el logo existente.
        """
        if self.instance is None and not attrs.get('logo'):
            raise serializers.ValidationError({
                'logo': (
                    'Debes seleccionar una imagen para el '
                    'logo del hotel.'
                ),
            })

        return attrs

    def create(self, validated_data):
        """
        Primero crea el hotel para obtener su ID.

        Después guarda el logo, permitiendo que `upload_to`
        genere una ruta como hoteles/5/imagen.png en lugar
        de hoteles/sin-hotel/imagen.png.
        """
        logo = validated_data.pop('logo', None)

        hotel = Hotel.objects.create(
            **validated_data,
        )

        if logo is not None:
            hotel.logo = logo
            hotel.save(
                update_fields=[
                    'logo',
                    'updated_at',
                ],
            )

        return hotel

    def get_logo_url(self, obj) -> str | None:
        """
        Devuelve una URL absoluta HTTPS para el logo.
        """
        if obj.logo:
            try:
                image_url = obj.logo.url
            except ValueError:
                image_url = None

            if image_url:
                request = self.context.get('request')

                if request is not None:
                    return request.build_absolute_uri(
                        image_url,
                    )

                return image_url

        return obj.logo_url or None