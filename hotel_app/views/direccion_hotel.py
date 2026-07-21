from rest_framework.viewsets import ModelViewSet

from hotel_app.models.direccion_hotel import DireccionHotel
from hotel_app.permissions import IsAdminOrReadOnly
from hotel_app.serializers.direccion_hotel import (
    DireccionHotelSerializer,
)


class DireccionHotelViewSet(ModelViewSet):
    queryset = DireccionHotel.objects.all()
    serializer_class = DireccionHotelSerializer
    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filterset_fields = [
        'hotel',
        'provincia',
        'ciudad',
    ]

    search_fields = [
        'provincia',
        'ciudad',
        'direccion',
        'referencia',
    ]

    ordering_fields = [
        'id',
        'ciudad',
        'created_at',
        'updated_at',
    ]

    ordering = [
        'id',
    ]