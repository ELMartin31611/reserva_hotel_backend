from rest_framework import serializers

from hotel_app.models import CargoEmpleado


class CargoEmpleadoSerializer(serializers.ModelSerializer):

    class Meta:
        model = CargoEmpleado
        fields = '__all__'