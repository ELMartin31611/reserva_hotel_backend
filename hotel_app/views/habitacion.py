from rest_framework.viewsets import ModelViewSet

from hotel_app.models.habitacion import Habitacion
from hotel_app.serializers.habitacion import HabitacionSerializer


class HabitacionViewSet(ModelViewSet):
    queryset = Habitacion.objects.all()
    serializer_class = HabitacionSerializer

    filterset_fields = [
        "hotel",
        "tipo_habitacion",
        "estado",
        "piso",
        "es_fumador",
    ]

    search_fields = [
        "numero",
        "estado",
        "descripcion",
        "observaciones",
    ]

    ordering_fields = [
        "id",
        "numero",
        "piso",
        "created_at",
        "updated_at",
    ]

    ordering = ["id"]