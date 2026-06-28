from rest_framework import serializers
from hotel_app.models.reserva_habitacion import ReservaHabitacion


class ReservaHabitacionSerializer(serializers.ModelSerializer):
    habitacion_numero = serializers.CharField(
        source='habitacion.numero',
        read_only=True
    )
    tipo_habitacion = serializers.CharField(
        source='habitacion.tipo_habitacion.nombre',
        read_only=True
    )

    class Meta:
        model = ReservaHabitacion
        fields = [
            'id',
            'reserva',
            'habitacion',
            'habitacion_numero',
            'tipo_habitacion',
            'tarifa',
            'precio_noche',
            'noches',
            'subtotal',
            'estado',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'precio_noche',
            'noches',
            'subtotal',
            'created_at',
            'updated_at',
        ]

    def validate(self, data):
        reserva = data.get('reserva')
        habitacion = data.get('habitacion')

        if reserva and habitacion:
            existe_cruce = ReservaHabitacion.objects.filter(
                habitacion=habitacion,
                reserva__estado__in=['pendiente', 'confirmada'],
                reserva__fecha_entrada__lt=reserva.fecha_salida,
                reserva__fecha_salida__gt=reserva.fecha_entrada,
            )

            if self.instance:
                existe_cruce = existe_cruce.exclude(id=self.instance.id)

            if existe_cruce.exists():
                raise serializers.ValidationError(
                    'La habitación ya está reservada en ese rango de fechas.'
                )

        return data