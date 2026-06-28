from rest_framework import serializers

from hotel_app.models import DireccionCliente


class DireccionClienteSerializer(serializers.ModelSerializer):

    class Meta:
        model = DireccionCliente
        fields = '__all__'