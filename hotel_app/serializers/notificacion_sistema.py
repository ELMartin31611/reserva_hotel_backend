from rest_framework import serializers
from hotel_app.models.notificacion_sistema import NotificacionSistema


class NotificacionSistemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificacionSistema
        fields = [
            'id',
            'titulo',
            'mensaje',
            'tipo',
            'fecha_inicio',
            'fecha_fin',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
        ]

    def validate(self, data):
        fecha_inicio = data.get(
            'fecha_inicio',
            getattr(self.instance, 'fecha_inicio', None)
        )
        fecha_fin = data.get(
            'fecha_fin',
            getattr(self.instance, 'fecha_fin', None)
        )

        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise serializers.ValidationError({
                'fecha_fin': 'La fecha fin no puede ser menor que la fecha de inicio.'
            })

        return data