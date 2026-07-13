from pathlib import Path
from uuid import uuid4

from django.db import models

from hotel_app.models.habitacion import Habitacion
from hotel_app.validators import validate_image_file


def habitacion_image_upload_path(instance, filename):
    extension = Path(filename).suffix.lower()
    habitacion_id = instance.habitacion_id or 'sin-habitacion'
    unique_name = f'{uuid4().hex}{extension}'

    return (
        f'habitaciones/'
        f'{habitacion_id}/'
        f'{unique_name}'
    )


class ImagenHabitacion(models.Model):
    habitacion = models.ForeignKey(
        Habitacion,
        on_delete=models.CASCADE,
        related_name='imagenes',
    )

    imagen_url = models.ImageField(
        upload_to=habitacion_image_upload_path,
        max_length=255,
        validators=[validate_image_file],
    )

    titulo = models.CharField(
        max_length=100,
    )

    descripcion = models.TextField(
        blank=True,
        default='',
    )

    orden = models.PositiveIntegerField(
        default=0,
    )

    es_principal = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = 'imagen_habitacion'
        verbose_name = 'Imagen de Habitación'
        verbose_name_plural = 'Imágenes de Habitación'
        ordering = [
            'orden',
            'id',
        ]

    def __str__(self):
        return (
            f'{self.habitacion.numero} - '
            f'{self.titulo}'
        )