from rest_framework import viewsets
from hotel_app.models.temporada import Temporada
from hotel_app.serializers.temporada import TemporadaSerializer
from hotel_app.permissions import IsAdminOrReadOnly


class TemporadaViewSet(viewsets.ModelViewSet):
    queryset = Temporada.objects.all()
    serializer_class = TemporadaSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = ['is_active']
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['id', 'nombre', 'fecha_inicio', 'fecha_fin']
    ordering = ['fecha_inicio']