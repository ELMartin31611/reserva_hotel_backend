from rest_framework import serializers
from hotel_app.models.temporada import Temporada


class TemporadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Temporada
        fields = [
            'id',
            'nombre',
            'fecha_inicio',
            'fecha_fin',
            'porcentaje_incremento',
            'descripcion',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        fecha_inicio = data.get(
            'fecha_inicio',
            getattr(self.instance, 'fecha_inicio', None)
        )
        fecha_fin = data.get(
            'fecha_fin',
            getattr(self.instance, 'fecha_fin', None)
        )

        if fecha_inicio and fecha_fin and fecha_fin <= fecha_inicio:
            raise serializers.ValidationError(
                'La fecha fin debe ser mayor que la fecha de inicio.'
            )

        return data
    