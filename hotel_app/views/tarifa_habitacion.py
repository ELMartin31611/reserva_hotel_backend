from rest_framework import viewsets
from hotel_app.models.tarifa_habitacion import TarifaHabitacion
from hotel_app.serializers.tarifa_habitacion import TarifaHabitacionSerializer
from hotel_app.permissions import IsAdminOrReadOnly


class TarifaHabitacionViewSet(viewsets.ModelViewSet):
    queryset = TarifaHabitacion.objects.select_related(
        'tipo_habitacion',
        'temporada'
    ).all()
    serializer_class = TarifaHabitacionSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = [
        'tipo_habitacion',
        'temporada',
        'is_active',
        'moneda',
    ]
    search_fields = [
        'tipo_habitacion__nombre',
        'temporada__nombre',
    ]
    ordering_fields = [
        'id',
        'precio_noche',
        'precio_fin_semana',
        'created_at',
    ]
    ordering = ['id']