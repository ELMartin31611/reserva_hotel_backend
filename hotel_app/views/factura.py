from rest_framework import viewsets
from rest_framework.permissions import (
    IsAuthenticated,
)

from hotel_app.models import Factura
from hotel_app.permissions import (
    user_is_admin,
)
from hotel_app.serializers.factura import (
    FacturaSerializer,
)


class FacturaViewSet(
    viewsets.ReadOnlyModelViewSet
):
    serializer_class = FacturaSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    filterset_fields = [
        'estado',
        'reserva',
    ]
    search_fields = [
        'numero_factura',
        'reserva__codigo',
        'cliente__nombres',
        'cliente__apellidos',
    ]
    ordering_fields = [
        'id',
        'fecha_emision',
        'total',
    ]
    ordering = ['-fecha_emision']

    def get_queryset(self):
        if getattr(
            self,
            'swagger_fake_view',
            False,
        ):
            return Factura.objects.none()

        queryset = (
            Factura.objects.select_related(
                'reserva',
                'cliente',
                'cliente__perfil',
            )
        )

        if user_is_admin(
            self.request.user
        ):
            return queryset

        return queryset.filter(
            cliente__perfil__user=(
                self.request.user
            ),
        )