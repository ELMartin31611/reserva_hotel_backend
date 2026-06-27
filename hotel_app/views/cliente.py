from rest_framework import viewsets

from hotel_app.models import (
    Cliente,
    DireccionCliente,
    DocumentoCliente
)

from hotel_app.serializers import (
    ClienteSerializer,
    DireccionClienteSerializer,
    DocumentoClienteSerializer
)


class ClienteViewSet(viewsets.ModelViewSet):

    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer


class DireccionClienteViewSet(viewsets.ModelViewSet):

    queryset = DireccionCliente.objects.all()
    serializer_class = DireccionClienteSerializer


class DocumentoClienteViewSet(viewsets.ModelViewSet):

    queryset = DocumentoCliente.objects.all()
    serializer_class = DocumentoClienteSerializer