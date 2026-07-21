from rest_framework.viewsets import ModelViewSet

from hotel_app.models.cama import Cama
from hotel_app.permissions import IsAdminOrReadOnly
from hotel_app.serializers.cama import CamaSerializer


class CamaViewSet(ModelViewSet):
    queryset = Cama.objects.all()
    serializer_class = CamaSerializer
    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filterset_fields = [
        'is_active',
        'capacidad_personas',
    ]

    search_fields = [
        'nombre',
        'descripcion',
    ]

    ordering_fields = [
        'id',
        'nombre',
        'capacidad_personas',
        'created_at',
        'updated_at',
    ]

    ordering = [
        'id',
    ]