from rest_framework import serializers

from hotel_app.models import ReservaServicio


class ReservaServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservaServicio
        fields = [
            'id',
            'reserva',
            'servicio',
            'nombre',
            'cantidad',
            'precio_unitario',
            'subtotal',
            'moneda',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields
