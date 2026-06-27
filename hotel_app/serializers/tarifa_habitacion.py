from rest_framework import serializers
from hotel_app.models.tarifa_habitacion import TarifaHabitacion


class TarifaHabitacionSerializer(serializers.ModelSerializer):
    tipo_habitacion_nombre = serializers.CharField(
        source='tipo_habitacion.nombre',
        read_only=True
    )
    temporada_nombre = serializers.CharField(
        source='temporada.nombre',
        read_only=True
    )

    class Meta:
        model = TarifaHabitacion
        fields = [
            'id',
            'tipo_habitacion',
            'tipo_habitacion_nombre',
            'temporada',
            'temporada_nombre',
            'precio_noche',
            'precio_fin_semana',
            'precio_persona_extra',
            'moneda',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_precio_noche(self, value):
        if value < 0:
            raise serializers.ValidationError(
                'El precio por noche no puede ser negativo.'
            )
        return value