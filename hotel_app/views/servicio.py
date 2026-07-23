from django.db import IntegrityError
from django.db.models import ProtectedError
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from hotel_app.models import Servicio, ReservaServicio
from hotel_app.permissions import IsAdminOrReadOnly
from hotel_app.serializers.servicio import ServicioSerializer


class ServicioViewSet(ModelViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer
    permission_classes = [
        IsAdminOrReadOnly,
    ]
    parser_classes = [
        MultiPartParser,
        FormParser,
        JSONParser,
    ]

    filterset_fields = [
        'tipo_servicio',
        'is_active',
    ]

    search_fields = [
        'nombre',
        'descripcion',
        'tipo_servicio',
        'icono',
    ]

    ordering_fields = [
        'id',
        'nombre',
        'precio_extra',
        'created_at',
        'updated_at',
    ]

    ordering = [
        'id',
    ]

    def destroy(self, request, *args, **kwargs):
        service = self.get_object()

        has_reservation_history = ReservaServicio.objects.filter(
            servicio=service
        ).exists()

        if not has_reservation_history:
            try:
                service.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except (ProtectedError, IntegrityError):
                pass

        # Desactivación lógica para proteger historial financiero
        service.is_active = False
        service.save(update_fields=['is_active', 'updated_at'])

        return Response(status=status.HTTP_204_NO_CONTENT)