from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from hotel_app.models.factura import Factura
from hotel_app.serializers.factura import FacturaSerializer
from hotel_app.permissions import IsReservaOwnerOrAdmin


class FacturaViewSet(viewsets.ModelViewSet):
    serializer_class = FacturaSerializer
    permission_classes = [IsAuthenticated, IsReservaOwnerOrAdmin]

    filterset_fields = ['estado', 'cliente', 'reserva']
    search_fields = [
        'numero_factura',
        'reserva__codigo',
        'cliente__nombres',
        'cliente__apellidos',
    ]
    ordering_fields = ['id', 'fecha_emision', 'total']
    ordering = ['-fecha_emision']

    def get_queryset(self):
        queryset = Factura.objects.select_related(
            'reserva',
            'cliente',
            'cliente__perfil'
        )

        if self.request.user.is_staff:
            return queryset

        return queryset.filter(
            cliente__perfil__user=self.request.user
        )