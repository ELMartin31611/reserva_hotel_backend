from rest_framework import viewsets

from hotel_app.models import EmpleadoTurno

from hotel_app.serializers import (
    EmpleadoTurnoSerializer
)


class EmpleadoTurnoViewSet(viewsets.ModelViewSet):

    queryset = EmpleadoTurno.objects.all()
    serializer_class = EmpleadoTurnoSerializer