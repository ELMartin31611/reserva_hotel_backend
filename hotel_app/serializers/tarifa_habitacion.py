from decimal import Decimal

from rest_framework import serializers

from hotel_app.models.tarifa_habitacion import TarifaHabitacion


class TarifaHabitacionSerializer(serializers.ModelSerializer):
    """
    Serializer para las tarifas asociadas a un tipo de habitación.

    Incluye nombres descriptivos y calcula el precio aplicable
    dependiendo de si la fecha consultada corresponde a un fin
    de semana.
    """

    tipo_habitacion_nombre = serializers.CharField(
        source='tipo_habitacion.nombre',
        read_only=True,
    )
    temporada_nombre = serializers.CharField(
        source='temporada.nombre',
        read_only=True,
    )
    temporada_fecha_inicio = serializers.DateField(
        source='temporada.fecha_inicio',
        read_only=True,
    )
    temporada_fecha_fin = serializers.DateField(
        source='temporada.fecha_fin',
        read_only=True,
    )
    precio_aplicable = serializers.SerializerMethodField()

    class Meta:
        model = TarifaHabitacion
        fields = [
            'id',
            'tipo_habitacion',
            'tipo_habitacion_nombre',
            'temporada',
            'temporada_nombre',
            'temporada_fecha_inicio',
            'temporada_fecha_fin',
            'precio_noche',
            'precio_fin_semana',
            'precio_persona_extra',
            'precio_aplicable',
            'moneda',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'created_at',
            'updated_at',
        ]

    def validate_precio_noche(self, value):
        """
        Impide guardar precios negativos.
        """
        if value < 0:
            raise serializers.ValidationError(
                'El precio por noche no puede ser negativo.',
            )

        return value

    def validate_precio_fin_semana(self, value):
        """
        El precio de fin de semana puede ser nulo,
        pero nunca puede ser negativo.
        """
        if value is not None and value < 0:
            raise serializers.ValidationError(
                'El precio de fin de semana no puede ser negativo.',
            )

        return value

    def validate_precio_persona_extra(self, value):
        """
        El precio por persona adicional puede ser nulo,
        pero nunca puede ser negativo.
        """
        if value is not None and value < 0:
            raise serializers.ValidationError(
                'El precio por persona adicional no puede ser negativo.',
            )

        return value

    def get_precio_aplicable(
        self,
        obj: TarifaHabitacion,
    ) -> Decimal:
        """
        Devuelve el precio de fin de semana cuando la fecha
        consultada es sábado o domingo.

        En cualquier otro caso devuelve el precio normal.
        """
        fecha = self.context.get('fecha')

        if (
            fecha is not None
            and fecha.weekday() >= 5
            and obj.precio_fin_semana is not None
        ):
            return obj.precio_fin_semana

        return obj.precio_noche


class TarifaVigenteQuerySerializer(serializers.Serializer):
    """
    Valida los parámetros usados para consultar una tarifa vigente.
    """

    tipo_habitacion = serializers.IntegerField(
        min_value=1,
    )
    fecha = serializers.DateField()