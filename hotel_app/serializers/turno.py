from rest_framework import serializers

from hotel_app.models import Turno


class TurnoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Turno
        fields = '__all__'