from rest_framework import viewsets
from hotel_app.models.tipo_habitacion_servicio import TipoHabitacionServicio
from hotel_app.serializers.tipo_habitacion_servicio import TipoHabitacionServicioSerializer
from hotel_app.permissions import IsAdminOrReadOnly


class TipoHabitacionServicioViewSet(viewsets.ModelViewSet):
    queryset = TipoHabitacionServicio.objects.select_related(
        'tipo_habitacion',
        'servicio'
    ).all()
    serializer_class = TipoHabitacionServicioSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = ['tipo_habitacion', 'servicio', 'incluido']
    search_fields = [
        'tipo_habitacion__nombre',
        'servicio__nombre',
    ]
    ordering_fields = ['id', 'created_at', 'precio_personalizado']
    ordering = ['id']