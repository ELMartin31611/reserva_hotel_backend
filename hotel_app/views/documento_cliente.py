from rest_framework import viewsets

from hotel_app.models import DocumentoCliente
from hotel_app.serializers import DocumentoClienteSerializer


class DocumentoClienteViewSet(viewsets.ModelViewSet):

    queryset = DocumentoCliente.objects.all()
    serializer_class = DocumentoClienteSerializer