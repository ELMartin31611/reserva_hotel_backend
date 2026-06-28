from rest_framework import serializers

from hotel_app.models.direccion_hotel import DireccionHotel


class DireccionHotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DireccionHotel
        fields = "__all__"