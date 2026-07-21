from rest_framework.parsers import (
    FormParser,
    JSONParser,
    MultiPartParser,
)
from rest_framework.viewsets import ModelViewSet

from hotel_app.models.hotel import Hotel
from hotel_app.permissions import IsAdminOrReadOnly
from hotel_app.serializers.hotel import HotelSerializer


class HotelViewSet(ModelViewSet):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [
        IsAdminOrReadOnly,
    ]

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

    ordering = [
        'id',
    ]