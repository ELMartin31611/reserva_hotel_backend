from rest_framework import serializers

from hotel_app.models import EmpleadoTurno


class EmpleadoTurnoSerializer(serializers.ModelSerializer):

    class Meta:
        model = EmpleadoTurno
        fields = '__all__'