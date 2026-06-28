from rest_framework import serializers

from hotel_app.models.cama import Cama


class CamaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cama
        fields = "__all__"