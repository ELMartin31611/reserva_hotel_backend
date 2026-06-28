from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from hotel_app.models.reserva import Reserva
from hotel_app.serializers.reserva import ReservaSerializer
from hotel_app.permissions import IsReservaOwnerOrAdmin


class ReservaViewSet(viewsets.ModelViewSet):
    serializer_class = ReservaSerializer
    permission_classes = [IsAuthenticated, IsReservaOwnerOrAdmin]

    filterset_fields = ['estado', 'cliente']
    search_fields = ['codigo', 'cliente__nombres', 'cliente__apellidos']
    ordering_fields = ['id', 'fecha_entrada', 'fecha_salida', 'created_at', 'total']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Reserva.objects.select_related(
            'cliente',
            'cliente__perfil',
            'cliente__perfil__user'
        )

        if self.request.user.is_staff:
            return queryset

        return queryset.filter(cliente__perfil__user=self.request.user)