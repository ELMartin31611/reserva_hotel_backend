from rest_framework import serializers

from hotel_app.models.tipo_habitacion import (
    TipoHabitacion,
)


class TipoHabitacionSerializer(
    serializers.ModelSerializer
):
    capacidad_maxima = serializers.IntegerField(
        read_only=True,
    )

    class Meta:
        model = TipoHabitacion
        fields = [
            'id',
            'hotel',
            'nombre',
            'descripcion',
            'capacidad_adultos',
            'capacidad_ninos',
            'capacidad_total',
            'capacidad_extra',
            'capacidad_maxima',
            'tamano_m2',
            'precio_base',
            'estado',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'capacidad_maxima',
            'created_at',
            'updated_at',
        ]

    def validate(self, attrs):
        adults = attrs.get(
            'capacidad_adultos',
            getattr(
                self.instance,
                'capacidad_adultos',
                0,
            ),
        )
        children = attrs.get(
            'capacidad_ninos',
            getattr(
                self.instance,
                'capacidad_ninos',
                0,
            ),
        )
        total = attrs.get(
            'capacidad_total',
            getattr(
                self.instance,
                'capacidad_total',
                0,
            ),
        )
        extra = attrs.get(
            'capacidad_extra',
            getattr(
                self.instance,
                'capacidad_extra',
                0,
            ),
        )
        size = attrs.get(
            'tamano_m2',
            getattr(
                self.instance,
                'tamano_m2',
                0,
            ),
        )
        base_price = attrs.get(
            'precio_base',
            getattr(
                self.instance,
                'precio_base',
                0,
            ),
        )

        errors = {}

        if adults < 1:
            errors['capacidad_adultos'] = (
                'Debe admitirse al menos un adulto.'
            )

        if children < 0:
            errors['capacidad_ninos'] = (
                'No puede ser negativa.'
            )

        if total < 1:
            errors['capacidad_total'] = (
                'Debe ser mayor que cero.'
            )
        elif total < adults + children:
            errors['capacidad_total'] = (
                'Debe cubrir la suma de adultos y niños.'
            )

        if extra < 0:
            errors['capacidad_extra'] = (
                'No puede ser negativa.'
            )

        if size <= 0:
            errors['tamano_m2'] = (
                'Debe ser mayor que cero.'
            )

        if base_price < 0:
            errors['precio_base'] = (
                'No puede ser negativo.'
            )

        if errors:
            raise serializers.ValidationError(
                errors
            )

        return attrs