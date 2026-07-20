from rest_framework import serializers

from hotel_app.models import HuespedReserva


class HuespedReservaSerializer(
    serializers.ModelSerializer,
):
    reserva_codigo = serializers.CharField(
        source='reserva.codigo',
        read_only=True,
    )
    habitacion_id = serializers.IntegerField(
        source=(
            'reserva_habitacion.habitacion_id'
        ),
        read_only=True,
    )
    habitacion_numero = serializers.CharField(
        source=(
            'reserva_habitacion.habitacion.numero'
        ),
        read_only=True,
    )

    class Meta:
        model = HuespedReserva
        fields = [
            'id',
            'reserva',
            'reserva_codigo',
            'reserva_habitacion',
            'habitacion_id',
            'habitacion_numero',
            'tipo_huesped',
            'nombres',
            'apellidos',
            'tipo_documento',
            'numero_documento',
            'edad',
            'telefono',
            'es_titular',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields