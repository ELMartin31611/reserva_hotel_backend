from rest_framework import viewsets

from hotel_app.models import Empleado

from hotel_app.serializers import (
    EmpleadoSerializer
)


class EmpleadoViewSet(viewsets.ModelViewSet):

    queryset = Empleado.objects.all()
    serializer_class = EmpleadoSerializer