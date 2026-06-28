from rest_framework import serializers

from hotel_app.models.habitacion import Habitacion


class HabitacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Habitacion
        fields = "__all__"