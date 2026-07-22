from django.db import IntegrityError
from django.db.models import (
    Exists,
    F,
    OuterRef,
    Prefetch,
    ProtectedError,
)
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from hotel_app.models import (
    Habitacion,
    ImagenHabitacion,
    ReservaHabitacion,
    TipoHabitacionServicio,
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
    'eliminada',
    'eliminado',
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
        return (
            Habitacion.objects
            .exclude(
                estado__iexact='eliminada',
            )
            .exclude(
                estado__iexact='eliminado',
            )
            .select_related(
                'hotel',
                'tipo_habitacion',
            )
            .prefetch_related(
                Prefetch(
                    'imagenes',
                    queryset=(
                        ImagenHabitacion.objects
                        .order_by(
                            '-es_principal',
                            'orden',
                            'id',
                        )
                    ),
                ),
                Prefetch(
                    'tipo_habitacion__servicios_habitacion',
                    queryset=(
                        TipoHabitacionServicio
                        .objects
                        .select_related('servicio')
                        .order_by('id')
                    ),
                ),
            )
            .order_by('id')
        )

    def destroy(
        self,
        request,
        *args,
        **kwargs,
    ):
        room = self.get_object()

        has_reservation_history = (
            ReservaHabitacion.objects
            .filter(habitacion=room)
            .exists()
        )

        if not has_reservation_history:
            try:
                room.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except (ProtectedError, IntegrityError):
                pass

        # Si tiene reservas o restricciones de FK, realiza borrado lógico.
        room.estado = 'eliminada'
        room.save(update_fields=['estado', 'updated_at'])

        return Response(status=status.HTTP_204_NO_CONTENT)

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
            ReservaHabitacion.objects
            .filter(
                habitacion_id=OuterRef('pk'),
                reserva__estado__in=[
                    'pendiente',
                    'confirmada',
                ],
                reserva__fecha_entrada__lt=params['fecha_salida'],
                reserva__fecha_salida__gt=params['fecha_entrada'],
            )
        )

        queryset = (
            self.get_queryset()
            .filter(
                hotel_id=params['hotel'],
            )
            .annotate(
                has_conflicting_reservation=Exists(
                    occupied_reservations,
                ),
            )
            .filter(
                has_conflicting_reservation=False,
            )
        )

        for room_state in NON_BOOKABLE_ROOM_STATES:
            queryset = queryset.exclude(
                estado__iexact=room_state,
            )
            queryset = queryset.exclude(
                hotel__estado__iexact=room_state,
            )
            queryset = queryset.exclude(
                tipo_habitacion__estado__iexact=room_state,
            )

        adults = params['cantidad_adultos']
        children = params['cantidad_ninos']

        total_guests = adults + children

        queryset = (
            queryset
            .annotate(
                calculated_maximum_capacity=(
                    F('tipo_habitacion__capacidad_total')
                    + F('tipo_habitacion__capacidad_extra')
                ),
            )
            .filter(
                calculated_maximum_capacity__gte=total_guests,
            )
        )

        if children > 0:
            queryset = queryset.filter(
                tipo_habitacion__capacidad_ninos__gt=0,
            )

        queryset = queryset.order_by('id')

        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(
            page if page is not None else queryset,
            many=True,
        )

        if page is not None:
            return self.get_paginated_response(serializer.data)

        return Response(serializer.data)