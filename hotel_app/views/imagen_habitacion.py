from rest_framework.parsers import (
    FormParser,
    JSONParser,
    MultiPartParser,
)
from rest_framework.viewsets import ModelViewSet

from hotel_app.models.imagen_habitacion import ImagenHabitacion
from hotel_app.permissions import IsAdminOrReadOnly
from hotel_app.serializers.imagen_habitacion import (
    ImagenHabitacionSerializer,
)


class ImagenHabitacionViewSet(ModelViewSet):
    queryset = ImagenHabitacion.objects.select_related(
        'habitacion',
        'habitacion__hotel',
        'habitacion__tipo_habitacion',
    ).all()

    serializer_class = ImagenHabitacionSerializer
    permission_classes = [IsAdminOrReadOnly]

    parser_classes = [
        MultiPartParser,
        FormParser,
        JSONParser,
    ]

    filterset_fields = [
        'habitacion',
        'es_principal',
    ]

    search_fields = [
        'titulo',
        'descripcion',
        'habitacion__numero',
    ]

    ordering_fields = [
        'id',
        'orden',
        'created_at',
        'updated_at',
    ]

    ordering = [
        'orden',
        'id',
    ]