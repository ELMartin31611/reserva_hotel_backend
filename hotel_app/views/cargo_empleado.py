from rest_framework import viewsets

from hotel_app.models import CargoEmpleado

from hotel_app.serializers import (
    CargoEmpleadoSerializer
)


class CargoEmpleadoViewSet(viewsets.ModelViewSet):

    queryset = CargoEmpleado.objects.all()
    serializer_class = CargoEmpleadoSerializer