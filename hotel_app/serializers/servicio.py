from rest_framework import serializers

from hotel_app.models.servicio import Servicio


class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = "__all__"