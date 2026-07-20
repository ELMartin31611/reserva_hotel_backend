from django.db.models import (
    Exists,
    OuterRef,
    Q,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from hotel_app.models import (
    Habitacion,
    ReservaHabitacion,
)
from hotel_app.permissions import IsAdminOrReadOnly
from hotel_app.serializers.habitacion import (
    AvailabilityQuerySerializer,
    HabitacionSerializer,
)


class HabitacionViewSet(ModelViewSet):
    serializer_class = HabitacionSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = [
        'hotel',
        'tipo_habitacion',
        'estado',
        'piso',
        'es_fumador',
    ]
    search_fields = [
        'numero',
        'estado',
        'descripcion',
        'observaciones',
    ]
    ordering_fields = [
        'id',
        'numero',
        'piso',
        'created_at',
        'updated_at',
    ]
    ordering = ['id']

    def get_queryset(self):
        return Habitacion.objects.select_related(
            'hotel',
            'tipo_habitacion',
        )

    @action(
        detail=False,
        methods=['get'],
        url_path='disponibles',
    )
    def disponibles(self, request):
        query = AvailabilityQuerySerializer(
            data=request.query_params,
        )
        query.is_valid(raise_exception=True)
        params = query.validated_data

        reservation_conflicts = (
            ReservaHabitacion.objects.filter(
                habitacion_id=OuterRef('pk'),
                reserva__estado__in=[
                    'pendiente',
                    'confirmada',
                ],
                reserva__fecha_entrada__lt=(
                    params['fecha_salida']
                ),
                reserva__fecha_salida__gt=(
                    params['fecha_entrada']
                ),
            )
        )

        unavailable_state = (
            Q(estado__iexact='mantenimiento')
            | Q(estado__iexact='en mantenimiento')
            | Q(estado__iexact='fuera de servicio')
            | Q(estado__iexact='fuera_servicio')
            | Q(estado__iexact='inactiva')
            | Q(estado__iexact='inactivo')
            | Q(estado__iexact='bloqueada')
            | Q(estado__iexact='bloqueado')
            | Q(estado__iexact='no disponible')
        )

        queryset = (
            self.get_queryset()
            .filter(
                hotel_id=params['hotel'],
            )
            .exclude(unavailable_state)
            .annotate(
                has_reservation_conflict=Exists(
                    reservation_conflicts,
                ),
            )
            .filter(
                has_reservation_conflict=False,
            )
        )

        adults = params.get(
            'cantidad_adultos',
        )
        children = params.get(
            'cantidad_ninos',
            0,
        )

        if adults is not None:
            queryset = queryset.filter(
                tipo_habitacion__capacidad_adultos__gte=(
                    adults
                ),
                tipo_habitacion__capacidad_ninos__gte=(
                    children
                ),
                tipo_habitacion__capacidad_total__gte=(
                    adults + children
                ),
            )

        queryset = queryset.order_by('id')

        page = self.paginate_queryset(
            queryset,
        )
        serializer = self.get_serializer(
            page
            if page is not None
            else queryset,
            many=True,
        )

        if page is not None:
            return self.get_paginated_response(
                serializer.data,
            )

        return Response(serializer.data)