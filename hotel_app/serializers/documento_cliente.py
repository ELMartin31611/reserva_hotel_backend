from rest_framework import serializers

from hotel_app.models import DocumentoCliente


class DocumentoClienteSerializer(serializers.ModelSerializer):

    class Meta:
        model = DocumentoCliente
        fields = '__all__'