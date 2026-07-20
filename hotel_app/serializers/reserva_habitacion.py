from rest_framework import serializers

from hotel_app.models import (
    ReservaHabitacion,
)


class ReservaHabitacionSerializer(
    serializers.ModelSerializer
):
    habitacion_numero = serializers.CharField(
        source='habitacion.numero',
        read_only=True,
    )
    tipo_habitacion = serializers.CharField(
        source=(
            'habitacion.tipo_habitacion.nombre'
        ),
        read_only=True,
    )
    hotel_id = serializers.IntegerField(
        source='habitacion.hotel_id',
        read_only=True,
    )
    hotel_nombre = serializers.CharField(
        source='habitacion.hotel.nombre',
        read_only=True,
    )

    class Meta:
        model = ReservaHabitacion
        fields = [
            'id',
            'reserva',
            'habitacion',
            'habitacion_numero',
            'tipo_habitacion',
            'hotel_id',
            'hotel_nombre',
            'tarifa',
            'precio_noche',
            'noches',
            'cantidad_adultos',
            'cantidad_ninos',
            'cantidad_huespedes_incluidos',
            'cantidad_huespedes_extra',
            'subtotal_habitacion',
            'subtotal_huespedes_extra',
            'subtotal_adultos',
            'subtotal_ninos',
            'subtotal',
            'detalle_tarifas',
            'moneda',
            'estado',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields