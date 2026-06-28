from rest_framework import serializers
from hotel_app.models.reserva import Reserva


class ReservaSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Reserva
        fields = [
            'id',
            'codigo',
            'cliente',
            'cliente_nombre',
            'fecha_entrada',
            'fecha_salida',
            'numero_noches',
            'cantidad_adultos',
            'cantidad_ninos',
            'estado',
            'subtotal',
            'impuestos',
            'descuento',
            'total',
            'observaciones',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'codigo',
            'numero_noches',
            'created_at',
            'updated_at',
        ]

    def get_cliente_nombre(self, obj):
        return f'{obj.cliente.nombres} {obj.cliente.apellidos}'

    def validate(self, data):
        fecha_entrada = data.get(
            'fecha_entrada',
            getattr(self.instance, 'fecha_entrada', None)
        )
        fecha_salida = data.get(
            'fecha_salida',
            getattr(self.instance, 'fecha_salida', None)
        )

        if fecha_entrada and fecha_salida and fecha_salida <= fecha_entrada:
            raise serializers.ValidationError(
                'La fecha de salida debe ser mayor que la fecha de entrada.'
            )

        return data