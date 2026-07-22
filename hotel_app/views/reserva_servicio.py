from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from hotel_app.models import ReservaServicio
from hotel_app.permissions import user_is_admin
from hotel_app.serializers.reserva_servicio import ReservaServicioSerializer


class ReservaServicioViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ReservaServicioSerializer
    permission_classes = [IsAuthenticated]

    filterset_fields = [
        'reserva',
        'servicio',
        'moneda',
    ]
    search_fields = [
        'nombre',
        'reserva__codigo',
    ]
    ordering_fields = [
        'id',
        'created_at',
        'subtotal',
    ]
    ordering = ['id']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ReservaServicio.objects.none()

        queryset = ReservaServicio.objects.select_related(
            'reserva',
            'servicio',
            'reserva__cliente',
            'reserva__cliente__perfil',
        )

        if user_is_admin(self.request.user):
            return queryset

        return queryset.filter(
            reserva__cliente__perfil__user=self.request.user
        )
