from django.utils import timezone
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from hotel_app.models.pago import Pago
from hotel_app.models.factura import Factura
from hotel_app.serializers.pago import PagoSerializer
from hotel_app.permissions import IsReservaOwnerOrAdmin, user_owns_reserva


class PagoViewSet(viewsets.ModelViewSet):
    serializer_class = PagoSerializer
    permission_classes = [IsAuthenticated, IsReservaOwnerOrAdmin]

    filterset_fields = ['reserva', 'metodo_pago', 'estado']
    search_fields = ['codigo_transaccion', 'reserva__codigo', 'referencia']
    ordering_fields = ['id', 'fecha_pago', 'monto', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Pago.objects.select_related(
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
                'No puedes pagar una reserva que no te pertenece.'
            )

        pago = serializer.save()

        if pago.estado == 'aprobado':
            pago.fecha_pago = timezone.now()
            pago.save()

            reserva.estado = 'confirmada'
            reserva.save()

            Factura.generar_desde_reserva(
                reserva=reserva,
                metodo_pago=pago.metodo_pago
            )