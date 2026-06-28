from rest_framework import serializers
from hotel_app.models.huesped_reserva import HuespedReserva


class HuespedReservaSerializer(serializers.ModelSerializer):
    reserva_codigo = serializers.CharField(
        source='reserva.codigo',
        read_only=True
    )

    class Meta:
        model = HuespedReserva
        fields = [
            'id',
            'reserva',
            'reserva_codigo',
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
        read_only_fields = ['created_at', 'updated_at']