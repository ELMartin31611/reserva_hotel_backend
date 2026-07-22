from django.db import IntegrityError
from django.db.models import ProtectedError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from hotel_app.models import TipoHabitacion, ReservaHabitacion
from hotel_app.permissions import IsAdminOrReadOnly
from hotel_app.serializers.tipo_habitacion import TipoHabitacionSerializer


class TipoHabitacionViewSet(ModelViewSet):
    queryset = TipoHabitacion.objects.all()
    serializer_class = TipoHabitacionSerializer
    permission_classes = [
        IsAdminOrReadOnly,
    ]

    filterset_fields = [
        'hotel',
        'estado',
        'capacidad_total',
    ]

    search_fields = [
        'nombre',
        'descripcion',
        'estado',
    ]

    ordering_fields = [
        'id',
        'nombre',
        'precio_base',
        'capacidad_total',
        'created_at',
        'updated_at',
    ]

    ordering = [
        'id',
    ]

    def destroy(self, request, *args, **kwargs):
        room_type = self.get_object()

        has_reservation_history = ReservaHabitacion.objects.filter(
            habitacion__tipo_habitacion=room_type
        ).exists()

        if not has_reservation_history:
            try:
                room_type.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except (ProtectedError, IntegrityError):
                pass

        # Desactivación lógica si existen reservas asociadas
        room_type.estado = 'inactivo'
        room_type.save(update_fields=['estado', 'updated_at'])

        return Response(status=status.HTTP_204_NO_CONTENT)