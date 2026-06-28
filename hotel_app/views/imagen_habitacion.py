from rest_framework.viewsets import ModelViewSet

from hotel_app.models.imagen_habitacion import ImagenHabitacion
from hotel_app.serializers.imagen_habitacion import ImagenHabitacionSerializer


class ImagenHabitacionViewSet(ModelViewSet):
    queryset = ImagenHabitacion.objects.all()
    serializer_class = ImagenHabitacionSerializer

    filterset_fields = [
        "habitacion",
        "es_principal",
    ]

    search_fields = [
        "titulo",
        "descripcion",
        "imagen_url",
    ]

    ordering_fields = [
        "id",
        "orden",
        "created_at",
        "updated_at",
    ]

    ordering = ["id"]