from rest_framework import serializers
from hotel_app.models.pago import Pago


class PagoSerializer(serializers.ModelSerializer):
    reserva_codigo = serializers.CharField(
        source='reserva.codigo',
        read_only=True
    )

    class Meta:
        model = Pago
        fields = [
            'id',
            'reserva',
            'reserva_codigo',
            'codigo_transaccion',
            'metodo_pago',
            'monto',
            'estado',
            'fecha_pago',
            'referencia',
            'comprobante_url',
            'observaciones',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'codigo_transaccion',
            'fecha_pago',
            'created_at',
            'updated_at',
        ]

    def validate(self, data):
        reserva = data.get('reserva')

        if reserva and reserva.estado == 'cancelada':
            raise serializers.ValidationError(
                'No se puede pagar una reserva cancelada.'
            )

        return data