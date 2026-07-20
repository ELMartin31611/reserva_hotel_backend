from rest_framework import viewsets
from rest_framework.permissions import (
    IsAuthenticated,
)

from hotel_app.models import HuespedReserva
from hotel_app.permissions import (
    IsReservaOwnerOrAdmin,
    user_is_admin,
)
from hotel_app.serializers.huesped_reserva import (
    HuespedReservaSerializer,
)


class HuespedReservaViewSet(
    viewsets.ReadOnlyModelViewSet,
):
    serializer_class = (
        HuespedReservaSerializer
    )
    permission_classes = [
        IsAuthenticated,
        IsReservaOwnerOrAdmin,
    ]

    filterset_fields = [
        'reserva',
        'reserva_habitacion',
        'tipo_huesped',
        'tipo_documento',
        'es_titular',
    ]
    search_fields = [
        'nombres',
        'apellidos',
        'numero_documento',
        'reserva__codigo',
    ]
    ordering_fields = [
        'id',
        'created_at',
    ]
    ordering = ['id']

    def get_queryset(self):
        if getattr(
            self,
            'swagger_fake_view',
            False,
        ):
            return HuespedReserva.objects.none()

        queryset = (
            HuespedReserva.objects
            .select_related(
                'reserva',
                'reserva__cliente',
                'reserva__cliente__perfil',
                'reserva_habitacion',
                (
                    'reserva_habitacion'
                    '__habitacion'
                ),
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