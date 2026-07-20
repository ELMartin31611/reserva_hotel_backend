from datetime import date

from rest_framework import serializers

from hotel_app.models import Habitacion


class HabitacionSerializer(serializers.ModelSerializer):
    hotel_nombre = serializers.CharField(
        source='hotel.nombre',
        read_only=True,
    )
    tipo_habitacion_nombre = serializers.CharField(
        source='tipo_habitacion.nombre',
        read_only=True,
    )
    capacidad_adultos = serializers.IntegerField(
        source='tipo_habitacion.capacidad_adultos',
        read_only=True,
    )
    capacidad_ninos = serializers.IntegerField(
        source='tipo_habitacion.capacidad_ninos',
        read_only=True,
    )
    capacidad_total = serializers.IntegerField(
        source='tipo_habitacion.capacidad_total',
        read_only=True,
    )

    class Meta:
        model = Habitacion
        fields = [
            'id',
            'hotel',
            'hotel_nombre',
            'tipo_habitacion',
            'tipo_habitacion_nombre',
            'capacidad_adultos',
            'capacidad_ninos',
            'capacidad_total',
            'numero',
            'piso',
            'estado',
            'descripcion',
            'es_fumador',
            'observaciones',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'created_at',
            'updated_at',
        ]

    def validate(self, attrs):
        hotel = attrs.get(
            'hotel',
            getattr(self.instance, 'hotel', None),
        )
        room_type = attrs.get(
            'tipo_habitacion',
            getattr(self.instance, 'tipo_habitacion', None),
        )
        number = attrs.get(
            'numero',
            getattr(self.instance, 'numero', ''),
        ).strip()

        if (
            hotel
            and room_type
            and room_type.hotel_id != hotel.id
        ):
            raise serializers.ValidationError({
                'tipo_habitacion': (
                    'El tipo de habitación no pertenece '
                    'al hotel elegido.'
                ),
            })

        duplicates = Habitacion.objects.filter(
            hotel=hotel,
            numero__iexact=number,
        )

        if self.instance:
            duplicates = duplicates.exclude(
                pk=self.instance.pk,
            )

        if hotel and number and duplicates.exists():
            raise serializers.ValidationError({
                'numero': (
                    'Ya existe esa habitación en el hotel.'
                ),
            })

        attrs['numero'] = number
        return attrs


class AvailabilityQuerySerializer(serializers.Serializer):
    hotel = serializers.IntegerField(min_value=1)
    fecha_entrada = serializers.DateField()
    fecha_salida = serializers.DateField()
    cantidad_adultos = serializers.IntegerField(
        min_value=1,
        required=False,
    )
    cantidad_ninos = serializers.IntegerField(
        min_value=0,
        required=False,
        default=0,
    )

    def validate(self, attrs):
        if attrs['fecha_entrada'] < date.today():
            raise serializers.ValidationError({
                'fecha_entrada': (
                    'La fecha de entrada no puede ser pasada.'
                ),
            })

        if attrs['fecha_salida'] <= attrs['fecha_entrada']:
            raise serializers.ValidationError({
                'fecha_salida': (
                    'La fecha de salida debe ser mayor '
                    'que la de entrada.'
                ),
            })

        nights = (
            attrs['fecha_salida']
            - attrs['fecha_entrada']
        ).days

        if nights > 30:
            raise serializers.ValidationError({
                'fecha_salida': (
                    'La estancia máxima es de 30 noches.'
                ),
            })

        return attrs