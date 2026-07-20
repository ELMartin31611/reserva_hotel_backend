from rest_framework import (
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
)
from rest_framework.response import Response

from hotel_app.models import Pago
from hotel_app.permissions import (
    user_is_admin,
)
from hotel_app.serializers.factura import (
    FacturaSerializer,
)
from hotel_app.serializers.pago import (
    PagoSerializer,
    ProcessPaymentInputSerializer,
)
from hotel_app.services.payment_processing import (
    PaymentProcessingService,
)


class PagoViewSet(
    viewsets.ReadOnlyModelViewSet
):
    serializer_class = PagoSerializer
    permission_classes = [
        IsAuthenticated,
    ]

    filterset_fields = [
        'reserva',
        'metodo_pago',
        'estado',
    ]
    search_fields = [
        'codigo_transaccion',
        'reserva__codigo',
        'referencia',
    ]
    ordering_fields = [
        'id',
        'fecha_pago',
        'monto',
        'created_at',
    ]
    ordering = ['-created_at']

    def get_queryset(self):
        if getattr(
            self,
            'swagger_fake_view',
            False,
        ):
            return Pago.objects.none()

        queryset = (
            Pago.objects.select_related(
                'reserva',
                'reserva__cliente',
                'reserva__cliente__perfil',
            )
        )

        if user_is_admin(
            self.request.user
        ):
            return queryset

        return queryset.filter(
            reserva__cliente__perfil__user=(
                self.request.user
            ),
        )

    @action(
        detail=False,
        methods=['post'],
        url_path='procesar',
    )
    def procesar(self, request):
        input_serializer = (
            ProcessPaymentInputSerializer(
                data=request.data,
            )
        )
        input_serializer.is_valid(
            raise_exception=True,
        )

        payment, invoice = (
            PaymentProcessingService()
            .process(
                user=request.user,
                reservation_id=(
                    input_serializer
                    .validated_data[
                        'reserva_id'
                    ]
                ),
                payment_method=(
                    input_serializer
                    .validated_data[
                        'metodo_pago'
                    ]
                ),
                reference=(
                    input_serializer
                    .validated_data.get(
                        'referencia',
                        '',
                    )
                ),
            )
        )

        payment_data = PagoSerializer(
            payment,
            context=(
                self
                .get_serializer_context()
            ),
        ).data

        invoice_data = FacturaSerializer(
            invoice,
            context=(
                self
                .get_serializer_context()
            ),
        ).data

        return Response(
            {
                'pago': payment_data,
                'factura': invoice_data,
            },
            status=status.HTTP_201_CREATED,
        )