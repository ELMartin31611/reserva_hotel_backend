from rest_framework.viewsets import ModelViewSet

from hotel_app.models.servicio import Servicio
from hotel_app.serializers.servicio import ServicioSerializer


class ServicioViewSet(ModelViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer

    filterset_fields = [
        "tipo_servicio",
        "is_active",
    ]

    search_fields = [
        "nombre",
        "descripcion",
        "tipo_servicio",
        "icono",
    ]

    ordering_fields = [
        "id",
        "nombre",
        "precio_extra",
        "created_at",
        "updated_at",
    ]

    ordering = ["id"]