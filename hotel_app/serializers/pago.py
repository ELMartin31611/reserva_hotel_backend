from rest_framework import serializers

from hotel_app.models import Pago


class ProcessPaymentInputSerializer(
    serializers.Serializer
):
    reserva_id = serializers.IntegerField(
        min_value=1,
    )
    metodo_pago = serializers.ChoiceField(
        choices=Pago.METODO_CHOICES,
    )
    referencia = serializers.CharField(
        max_length=120,
        required=False,
        allow_blank=True,
        default='',
    )

    def validate(self, attrs):
        method = attrs['metodo_pago']
        reference = (
            attrs.get('referencia', '')
            .strip()
        )

        if (
            method == 'transferencia'
            and not reference
        ):
            raise serializers.ValidationError({
                'referencia': (
                    'La referencia es obligatoria '
                    'para pagos por transferencia.'
                ),
            })

        attrs['referencia'] = reference
        return attrs


class PagoSerializer(
    serializers.ModelSerializer
):
    reserva_codigo = serializers.CharField(
        source='reserva.codigo',
        read_only=True,
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
            'moneda',
            'estado',
            'fecha_pago',
            'referencia',
            'comprobante_url',
            'observaciones',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields