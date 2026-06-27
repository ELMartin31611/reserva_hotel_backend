from rest_framework import serializers

from hotel_app.models import (
    Cliente,
    DireccionCliente,
    DocumentoCliente
)


class ClienteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cliente
        fields = '__all__'


class DireccionClienteSerializer(serializers.ModelSerializer):

    class Meta:
        model = DireccionCliente
        fields = '__all__'


class DocumentoClienteSerializer(serializers.ModelSerializer):

    class Meta:
        model = DocumentoCliente
        fields = '__all__'