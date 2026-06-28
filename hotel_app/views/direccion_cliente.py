from rest_framework import viewsets

from hotel_app.models import DireccionCliente
from hotel_app.serializers import DireccionClienteSerializer


class DireccionClienteViewSet(viewsets.ModelViewSet):

    queryset = DireccionCliente.objects.all()
    serializer_class = DireccionClienteSerializer