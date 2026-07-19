from rest_framework import serializers

from hotel_app.models.temporada import Temporada


class TemporadaSerializer(serializers.ModelSerializer):
    """
    Serializa las temporadas utilizadas para administrar las tarifas.

    También valida que las fechas sean correctas y que no existan
    temporadas activas superpuestas.
    """

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
        read_only_fields = [
            'created_at',
            'updated_at',
        ]

    def validate(self, data):
        fecha_inicio = data.get(
            'fecha_inicio',
            getattr(self.instance, 'fecha_inicio', None),
        )
        fecha_fin = data.get(
            'fecha_fin',
            getattr(self.instance, 'fecha_fin', None),
        )
        is_active = data.get(
            'is_active',
            getattr(self.instance, 'is_active', True),
        )

        if (
            fecha_inicio is not None
            and fecha_fin is not None
            and fecha_fin <= fecha_inicio
        ):
            raise serializers.ValidationError({
                'fecha_fin': (
                    'La fecha de finalización debe ser mayor '
                    'que la fecha de inicio.'
                ),
            })

        if (
            fecha_inicio is not None
            and fecha_fin is not None
            and is_active
        ):
            temporadas_superpuestas = Temporada.objects.filter(
                is_active=True,
                fecha_inicio__lt=fecha_fin,
                fecha_fin__gt=fecha_inicio,
            )

            if self.instance is not None:
                temporadas_superpuestas = (
                    temporadas_superpuestas.exclude(
                        pk=self.instance.pk,
                    )
                )

            if temporadas_superpuestas.exists():
                raise serializers.ValidationError({
                    'fecha_inicio': (
                        'Ya existe una temporada activa que se '
                        'cruza con este rango de fechas.'
                    ),
                })

        return data