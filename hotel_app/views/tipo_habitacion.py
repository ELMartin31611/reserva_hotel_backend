from rest_framework.viewsets import ModelViewSet

from hotel_app.models.tipo_habitacion import TipoHabitacion
from hotel_app.permissions import IsAdminOrReadOnly
from hotel_app.serializers.tipo_habitacion import (
    TipoHabitacionSerializer,
)


class TipoHabitacionViewSet(ModelViewSet):
    queryset = TipoHabitacion.objects.all()
    serializer_class = TipoHabitacionSerializer
    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filterset_fields = [
        'hotel',
        'estado',
        'capacidad_total',
    ]

    search_fields = [
        'nombre',
        'descripcion',
        'estado',
    ]

    ordering_fields = [
        'id',
        'nombre',
        'precio_base',
        'capacidad_total',
        'created_at',
        'updated_at',
    ]

    ordering = [
        'id',
    ]