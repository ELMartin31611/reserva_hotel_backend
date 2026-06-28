from rest_framework import viewsets

from hotel_app.models import Cliente
from hotel_app.serializers import ClienteSerializer


class ClienteViewSet(viewsets.ModelViewSet):

    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer