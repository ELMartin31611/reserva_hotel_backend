from rest_framework import serializers

from hotel_app.models.imagen_habitacion import ImagenHabitacion


class ImagenHabitacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagenHabitacion
        fields = "__all__"