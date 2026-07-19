from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from hotel_app.models.tarifa_habitacion import TarifaHabitacion
from hotel_app.permissions import IsAdminOrReadOnly
from hotel_app.serializers.tarifa_habitacion import (
    TarifaHabitacionSerializer,
    TarifaVigenteQuerySerializer,
)


class TarifaHabitacionViewSet(viewsets.ModelViewSet):
    """
    Endpoint para consultar y administrar tarifas.

    Incluye una acción adicional llamada `vigente` para buscar
    el precio aplicable a un tipo de habitación en una fecha.
    """

    queryset = TarifaHabitacion.objects.select_related(
        'tipo_habitacion',
        'temporada',
    ).all()
    serializer_class = TarifaHabitacionSerializer
    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filterset_fields = [
        'tipo_habitacion',
        'temporada',
        'is_active',
        'moneda',
    ]
    search_fields = [
        'tipo_habitacion__nombre',
        'temporada__nombre',
    ]
    ordering_fields = [
        'id',
        'precio_noche',
        'precio_fin_semana',
        'created_at',
    ]
    ordering = [
        'id',
    ]

    @action(
        detail=False,
        methods=['get'],
        url_path='vigente',
    )
    def vigente(self, request):
        """
        Devuelve la tarifa activa correspondiente a un tipo de
        habitación y una fecha específica.

        Ejemplo:
        /api/tarifas-habitacion/vigente/
            ?tipo_habitacion=1&fecha=2026-07-20
        """
        query_serializer = TarifaVigenteQuerySerializer(
            data=request.query_params,
        )
        query_serializer.is_valid(raise_exception=True)

        tipo_habitacion_id = query_serializer.validated_data[
            'tipo_habitacion'
        ]
        fecha = query_serializer.validated_data['fecha']

        tarifa = self.get_queryset().filter(
            tipo_habitacion_id=tipo_habitacion_id,
            is_active=True,
            temporada__is_active=True,
            temporada__fecha_inicio__lte=fecha,
            temporada__fecha_fin__gt=fecha,
        ).order_by(
            '-temporada__porcentaje_incremento',
            '-id',
        ).first()

        if tarifa is None:
            raise NotFound(
                'No existe una tarifa activa para esa fecha.',
            )

        serializer = self.get_serializer(
            tarifa,
            context={
                **self.get_serializer_context(),
                'fecha': fecha,
            },
        )

        return Response(serializer.data)