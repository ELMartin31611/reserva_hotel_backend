from rest_framework import viewsets

from hotel_app.models import Turno

from hotel_app.serializers import (
    TurnoSerializer
)


class TurnoViewSet(viewsets.ModelViewSet):

    queryset = Turno.objects.all()
    serializer_class = TurnoSerializer