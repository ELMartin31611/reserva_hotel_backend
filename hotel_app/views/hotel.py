from rest_framework import status
from rest_framework.parsers import (
    FormParser,
    JSONParser,
    MultiPartParser,
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from hotel_app.models import (
    Hotel,
    ReservaHabitacion,
)
from hotel_app.permissions import IsAdminOrReadOnly
from hotel_app.serializers.hotel import HotelSerializer


class HotelViewSet(ModelViewSet):
    serializer_class = HotelSerializer
    permission_classes = [IsAdminOrReadOnly]

    parser_classes = [
        MultiPartParser,
        FormParser,
        JSONParser,
    ]

    filterset_fields = [
        'estado',
        'categoria_estrellas',
        'permite_mascotas',
    ]

    search_fields = [
        'nombre',
        'ruc',
        'telefono',
        'email',
        'descripcion',
    ]

    ordering_fields = [
        'id',
        'nombre',
        'categoria_estrellas',
        'created_at',
        'updated_at',
    ]

    ordering = ['id']

    def get_queryset(self):
        return (
            Hotel.objects
            .exclude(estado__iexact='eliminado')
            .order_by('id')
        )

    def destroy(self, request, *args, **kwargs):
        hotel = self.get_object()

        has_reservation_history = (
            ReservaHabitacion.objects
            .filter(
                habitacion__hotel=hotel,
            )
            .exists()
        )

        if not has_reservation_history:
            hotel.delete()

            return Response(
                status=status.HTTP_204_NO_CONTENT,
            )

        # Conserva reservas, pagos y facturas,
        # pero retira el hotel del sistema.
        hotel.estado = 'eliminado'
        hotel.save(
            update_fields=[
                'estado',
                'updated_at',
            ],
        )

        hotel.habitaciones.update(
            estado='inactiva',
        )

        hotel.tipos_habitacion.update(
            estado='inactivo',
        )

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )