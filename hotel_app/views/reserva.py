from rest_framework import (
    status,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
)
from rest_framework.response import Response

from hotel_app.models import Reserva
from hotel_app.permissions import (
    IsReservaOwnerOrAdmin,
    user_is_admin,
)
from hotel_app.serializers.reserva import (
    CompleteReservationInputSerializer,
    ReservaDetailSerializer,
    ReservaSerializer,
)
from hotel_app.services.reservation_creation import (
    ReservationCreationService,
)


class ReservaViewSet(
    viewsets.ModelViewSet,
):
    permission_classes = [
        IsAuthenticated,
        IsReservaOwnerOrAdmin,
    ]
    http_method_names = [
        'get',
        'post',
        'head',
        'options',
    ]

    filterset_fields = [
        'estado',
    ]
    search_fields = [
        'codigo',
        'cliente__nombres',
        'cliente__apellidos',
    ]
    ordering_fields = [
        'id',
        'fecha_entrada',
        'fecha_salida',
        'created_at',
        'total',
    ]
    ordering = [
        '-created_at',
    ]

    def get_queryset(self):
        if getattr(
            self,
            'swagger_fake_view',
            False,
        ):
            return Reserva.objects.none()

        queryset = (
            Reserva.objects
            .select_related(
                'cliente',
                'cliente__perfil',
                'cliente__perfil__user',
            )
            .prefetch_related(
                (
                    'habitaciones_reservadas'
                    '__habitacion__hotel'
                ),
                (
                    'habitaciones_reservadas'
                    '__habitacion'
                    '__tipo_habitacion'
                ),
                (
                    'habitaciones_reservadas'
                    '__tarifa'
                ),
                (
                    'huespedes'
                    '__reserva_habitacion'
                    '__habitacion'
                ),
                'servicios',
            )
        )

        if user_is_admin(
            self.request.user,
        ):
            return queryset

        return queryset.filter(
            cliente__perfil__user=(
                self.request.user
            ),
        )

    def get_serializer_class(self):
        if self.action == 'crear_completa':
            return (
                CompleteReservationInputSerializer
            )

        if self.action == 'retrieve':
            return ReservaDetailSerializer

        return ReservaSerializer

    def create(
        self,
        request,
        *args,
        **kwargs,
    ):
        return Response(
            {
                'detail': (
                    'Usa POST '
                    '/api/reservas/crear-completa/ '
                    'para crear una reserva.'
                ),
            },
            status=(
                status.HTTP_405_METHOD_NOT_ALLOWED
            ),
        )

    @action(
        detail=False,
        methods=['post'],
        url_path='crear-completa',
    )
    def crear_completa(
        self,
        request,
    ):
        serializer = self.get_serializer(
            data=request.data,
        )
        serializer.is_valid(
            raise_exception=True,
        )

        reservation = (
            ReservationCreationService()
            .create(
                user=request.user,
                validated_data=(
                    serializer.validated_data
                ),
            )
        )

        output = ReservaDetailSerializer(
            reservation,
            context=(
                self.get_serializer_context()
            ),
        )

        return Response(
            output.data,
            status=status.HTTP_201_CREATED,
        )