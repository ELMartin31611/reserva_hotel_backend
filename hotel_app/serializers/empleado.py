from rest_framework import serializers

from hotel_app.models import Empleado


class EmpleadoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Empleado
        fields = '__all__'