from rest_framework import serializers
from hotel_app.models.factura import Factura


class FacturaSerializer(serializers.ModelSerializer):
    reserva_codigo = serializers.CharField(
        source='reserva.codigo',
        read_only=True
    )
    cliente_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Factura
        fields = [
            'id',
            'reserva',
            'reserva_codigo',
            'cliente',
            'cliente_nombre',
            'numero_factura',
            'fecha_emision',
            'descripcion',
            'fecha_entrada',
            'fecha_salida',
            'numero_noches',
            'subtotal',
            'impuestos',
            'descuento',
            'total',
            'metodo_pago',
            'estado',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'numero_factura',
            'fecha_emision',
            'created_at',
            'updated_at',
        ]

    def get_cliente_nombre(self, obj):
        return f'{obj.cliente.nombres} {obj.cliente.apellidos}'