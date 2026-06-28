from rest_framework import viewsets
from hotel_app.models.notificacion_sistema import NotificacionSistema
from hotel_app.serializers.notificacion_sistema import NotificacionSistemaSerializer
from hotel_app.permissions import IsAdminOrReadOnly


class NotificacionSistemaViewSet(viewsets.ModelViewSet):
    queryset = NotificacionSistema.objects.all()
    serializer_class = NotificacionSistemaSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = [
        'tipo',
        'is_active',
        'fecha_inicio',
        'fecha_fin',
    ]

    search_fields = [
        'titulo',
        'mensaje',
        'tipo',
    ]

    ordering_fields = [
        'id',
        'titulo',
        'tipo',
        'fecha_inicio',
        'fecha_fin',
        'created_at',
    ]

    ordering = ['-created_at']