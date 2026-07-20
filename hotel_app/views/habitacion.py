from django.db.models import (
    Exists,
    F,
    OuterRef,
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


NON_BOOKABLE_ROOM_STATES = {
    'mantenimiento',
    'inactiva',
    'inactivo',
    'ocupada',
    'ocupado',
    'bloqueada',
    'bloqueado',
    'fuera de servicio',
    'fuera_servicio',
}


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

        occupied_reservations = (
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

        queryset = (
            self.get_queryset()
            .filter(
                hotel_id=params['hotel'],
            )
            .annotate(
                has_conflicting_reservation=Exists(
                    occupied_reservations
                ),
            )
            .filter(
                has_conflicting_reservation=False,
            )
        )

        for state in NON_BOOKABLE_ROOM_STATES:
            queryset = queryset.exclude(
                estado__iexact=state,
            )

        adults = params.get(
            'cantidad_adultos'
        )
        children = params.get(
            'cantidad_ninos',
            0,
        )

        if adults is not None:
            total_guests = adults + children

            queryset = (
                queryset
                .annotate(
                    calculated_maximum_capacity=(
                        F(
                            'tipo_habitacion'
                            '__capacidad_total'
                        )
                        + F(
                            'tipo_habitacion'
                            '__capacidad_extra'
                        )
                    ),
                )
                .filter(
                    calculated_maximum_capacity__gte=(
                        total_guests
                    ),
                )
            )

            if children > 0:
                queryset = queryset.filter(
                    tipo_habitacion__capacidad_ninos__gt=0,
                )

        queryset = queryset.order_by('id')

        page = self.paginate_queryset(
            queryset
        )

        serializer = self.get_serializer(
            (
                page
                if page is not None
                else queryset
            ),
            many=True,
        )

        if page is not None:
            return self.get_paginated_response(
                serializer.data
            )

        return Response(serializer.data)