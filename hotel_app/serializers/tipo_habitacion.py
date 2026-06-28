from rest_framework import serializers

from hotel_app.models.tipo_habitacion import TipoHabitacion


class TipoHabitacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoHabitacion
        fields = "__all__"