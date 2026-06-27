from rest_framework import serializers
from hotel_app.models.tipo_habitacion_servicio import TipoHabitacionServicio


class TipoHabitacionServicioSerializer(serializers.ModelSerializer):
    tipo_habitacion_nombre = serializers.CharField(
        source='tipo_habitacion.nombre',
        read_only=True
    )
    servicio_nombre = serializers.CharField(
        source='servicio.nombre',
        read_only=True
    )

    class Meta:
        model = TipoHabitacionServicio
        fields = [
            'id',
            'tipo_habitacion',
            'tipo_habitacion_nombre',
            'servicio',
            'servicio_nombre',
            'incluido',
            'precio_personalizado',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_precio_personalizado(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError(
                'El precio personalizado no puede ser negativo.'
            )
        return value