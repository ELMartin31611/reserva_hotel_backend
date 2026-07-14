from pathlib import Path
from uuid import uuid4

from django.db import models

from hotel_app.validators import validate_image_file


def hotel_logo_upload_path(instance, filename):
    extension = Path(filename).suffix.lower()
    hotel_id = instance.id or 'sin-hotel'
    unique_name = f'{uuid4().hex}{extension}'

    return f'hoteles/{hotel_id}/{unique_name}'


class Hotel(models.Model):
    nombre = models.CharField(max_length=150)
    ruc = models.CharField(max_length=20)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(max_length=254)
    descripcion = models.TextField()
    categoria_estrellas = models.IntegerField()

    # Opcional: Flutter no pedirá una URL.
    sitio_web = models.URLField(
        max_length=255,
        blank=True,
        default='',
    )

    # Campo antiguo: se conserva por compatibilidad,
    # pero Flutter ya no lo enviará.
    logo_url = models.URLField(
        max_length=255,
        blank=True,
        default='',
    )

    # Imagen real elegida desde galería o archivos.
    logo = models.ImageField(
        upload_to=hotel_logo_upload_path,
        max_length=255,
        blank=True,
        null=True,
        validators=[validate_image_file],
    )

    estado = models.CharField(max_length=20)
    hora_check_in = models.TimeField()
    hora_check_out = models.TimeField()
    permite_mascotas = models.BooleanField(default=False)
    edad_minima_reserva = models.IntegerField()
    politica_cancelacion = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hotel'
        verbose_name = 'Hotel'
        verbose_name_plural = 'Hoteles'

    def __str__(self):
        return self.nombre