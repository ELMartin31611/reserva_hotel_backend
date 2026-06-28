from rest_framework.viewsets import ModelViewSet

from hotel_app.models.tipo_habitacion_cama import TipoHabitacionCama
from hotel_app.serializers.tipo_habitacion_cama import TipoHabitacionCamaSerializer


class TipoHabitacionCamaViewSet(ModelViewSet):
    queryset = TipoHabitacionCama.objects.all()
    serializer_class = TipoHabitacionCamaSerializer

    filterset_fields = [
        "tipo_habitacion",
        "cama",
        "cantidad",
    ]

    ordering_fields = [
        "id",
        "cantidad",
        "created_at",
        "updated_at",
    ]

    ordering = ["id"]