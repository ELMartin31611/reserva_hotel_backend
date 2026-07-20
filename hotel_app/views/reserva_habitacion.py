from rest_framework import viewsets
from rest_framework.permissions import (
    IsAuthenticated,
)

from hotel_app.models import (
    ReservaHabitacion,
)
from hotel_app.permissions import (
    IsReservaOwnerOrAdmin,
    user_is_admin,
)
from hotel_app.serializers.reserva_habitacion import (
    ReservaHabitacionSerializer,
)


class ReservaHabitacionViewSet(
    viewsets.ReadOnlyModelViewSet,
):
    serializer_class = (
        ReservaHabitacionSerializer
    )
    permission_classes = [
        IsAuthenticated,
        IsReservaOwnerOrAdmin,
    ]

    filterset_fields = [
        'reserva',
        'habitacion',
        'estado',
    ]
    search_fields = [
        'reserva__codigo',
        'habitacion__numero',
        'habitacion__hotel__nombre',
    ]
    ordering_fields = [
        'id',
        'created_at',
        'subtotal',
    ]
    ordering = ['id']

    def get_queryset(self):
        if getattr(
            self,
            'swagger_fake_view',
            False,
        ):
            return (
                ReservaHabitacion.objects.none()
            )

        queryset = (
            ReservaHabitacion.objects
            .select_related(
                'reserva',
                'reserva__cliente',
                'reserva__cliente__perfil',
                'habitacion',
                'habitacion__hotel',
                'habitacion__tipo_habitacion',
                'tarifa',
                'tarifa__temporada',
            )
        )

        if user_is_admin(
            self.request.user,
        ):
            return queryset

        return queryset.filter(
            reserva__cliente__perfil__user=(
                self.request.user
            ),
        )