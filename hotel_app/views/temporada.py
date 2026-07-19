from rest_framework import viewsets

from hotel_app.models.temporada import Temporada
from hotel_app.permissions import IsAdminOrReadOnly
from hotel_app.serializers.temporada import TemporadaSerializer


class TemporadaViewSet(viewsets.ModelViewSet):
    """
    Endpoint para consultar y administrar temporadas.

    La lectura es pública, pero crear, editar o eliminar
    requiere permisos de administrador.
    """

    queryset = Temporada.objects.all()
    serializer_class = TemporadaSerializer
    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filterset_fields = [
        'is_active',
    ]
    search_fields = [
        'nombre',
        'descripcion',
    ]
    ordering_fields = [
        'id',
        'nombre',
        'fecha_inicio',
        'fecha_fin',
        'created_at',
    ]
    ordering = [
        'fecha_inicio',
    ]