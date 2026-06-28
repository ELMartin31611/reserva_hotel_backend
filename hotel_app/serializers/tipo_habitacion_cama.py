from rest_framework import serializers

from hotel_app.models.tipo_habitacion_cama import TipoHabitacionCama


class TipoHabitacionCamaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoHabitacionCama
        fields = "__all__"