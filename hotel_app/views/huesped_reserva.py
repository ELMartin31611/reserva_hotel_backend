from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from hotel_app.models.huesped_reserva import HuespedReserva
from hotel_app.serializers.huesped_reserva import HuespedReservaSerializer
from hotel_app.permissions import IsReservaOwnerOrAdmin, user_owns_reserva


class HuespedReservaViewSet(viewsets.ModelViewSet):
    serializer_class = HuespedReservaSerializer
    permission_classes = [IsAuthenticated, IsReservaOwnerOrAdmin]

    filterset_fields = ['reserva', 'tipo_documento', 'es_titular']
    search_fields = ['nombres', 'apellidos', 'numero_documento']
    ordering_fields = ['id', 'created_at']
    ordering = ['id']

    def get_queryset(self):
        queryset = HuespedReserva.objects.select_related(
            'reserva',
            'reserva__cliente',
            'reserva__cliente__perfil'
        )

        if self.request.user.is_staff:
            return queryset

        return queryset.filter(
            reserva__cliente__perfil__user=self.request.user
        )

    def perform_create(self, serializer):
        reserva = serializer.validated_data.get('reserva')

        if not user_owns_reserva(self.request.user, reserva):
            raise PermissionDenied(
                'No puedes agregar huéspedes a una reserva que no te pertenece.'
            )

        serializer.save()