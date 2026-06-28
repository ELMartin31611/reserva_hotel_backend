from django.db import models

from hotel_app.models.habitacion import Habitacion


class ImagenHabitacion(models.Model):
    habitacion = models.ForeignKey(
        Habitacion,
        on_delete=models.CASCADE,
        related_name="imagenes"
    )

    imagen_url = models.URLField(max_length=255)
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField()
    orden = models.IntegerField()
    es_principal = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "imagen_habitacion"
        verbose_name = "Imagen de Habitación"
        verbose_name_plural = "Imágenes de Habitación"

    def __str__(self):
        return f"{self.habitacion.numero} - {self.titulo}"