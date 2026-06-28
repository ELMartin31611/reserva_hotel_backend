from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from hotel_app.models.reserva_habitacion import ReservaHabitacion
from hotel_app.serializers.reserva_habitacion import ReservaHabitacionSerializer
from hotel_app.permissions import IsReservaOwnerOrAdmin, user_owns_reserva


class ReservaHabitacionViewSet(viewsets.ModelViewSet):
    serializer_class = ReservaHabitacionSerializer
    permission_classes = [IsAuthenticated, IsReservaOwnerOrAdmin]

    filterset_fields = ['reserva', 'habitacion', 'estado']
    search_fields = ['reserva__codigo', 'habitacion__numero']
    ordering_fields = ['id', 'created_at', 'subtotal']
    ordering = ['id']

    def get_queryset(self):
        queryset = ReservaHabitacion.objects.select_related(
            'reserva',
            'reserva__cliente',
            'reserva__cliente__perfil',
            'habitacion',
            'tarifa'
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
                'No puedes agregar habitaciones a una reserva que no te pertenece.'
            )

        serializer.save()