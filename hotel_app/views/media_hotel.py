from rest_framework.parsers import (
    FormParser,
    JSONParser,
    MultiPartParser,
)
from rest_framework.viewsets import ModelViewSet

from hotel_app.models import MediaHotel
from hotel_app.permissions import IsAdminOrReadOnly
from hotel_app.serializers.media_hotel import MediaHotelSerializer


class MediaHotelViewSet(ModelViewSet):
    serializer_class = MediaHotelSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = [
        MultiPartParser,
        FormParser,
        JSONParser,
    ]
    filterset_fields = ['hotel', 'tipo', 'es_principal']
    search_fields = ['titulo', 'descripcion', 'hotel__nombre']
    ordering_fields = ['id', 'orden', 'created_at', 'updated_at']
    ordering = ['orden', 'id']

    def get_queryset(self):
        return MediaHotel.objects.select_related('hotel').all()
