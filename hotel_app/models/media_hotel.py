from pathlib import Path
from uuid import uuid4

from django.db import models

from hotel_app.validators import (
    validate_hotel_media_file,
)


def hotel_media_upload_path(instance, filename):
    extension = Path(filename).suffix.lower()
    hotel_id = instance.hotel_id or 'sin-hotel'
    return (
        f'hoteles/{hotel_id}/galeria/'
        f'{uuid4().hex}{extension}'
    )


class MediaHotel(models.Model):
    TIPO_CHOICES = [
        ('imagen', 'Imagen'),
        ('video', 'Video'),
    ]

    hotel = models.ForeignKey(
        'hotel_app.Hotel',
        on_delete=models.CASCADE,
        related_name='media',
    )
    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES,
    )
    archivo = models.FileField(
        upload_to=hotel_media_upload_path,
        max_length=255,
        validators=[validate_hotel_media_file],
    )
    titulo = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, default='')
    orden = models.PositiveIntegerField(default=0)
    es_principal = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'media_hotel'
        ordering = ['orden', 'id']
        verbose_name = 'Media de hotel'
        verbose_name_plural = 'Media de hoteles'

    def __str__(self):
        return f'{self.hotel.nombre} - {self.titulo}'
