from pathlib import Path
from uuid import uuid4

from django.db import models

from hotel_app.validators import validate_image_file


def service_image_upload_path(instance, filename):
    extension = Path(filename).suffix.lower()
    return f'servicios/{instance.id or "nuevo"}/{uuid4().hex}{extension}'


class Servicio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    tipo_servicio = models.CharField(max_length=30)
    precio_extra = models.DecimalField(max_digits=10, decimal_places=2)
    icono = models.CharField(max_length=80)
    imagen = models.ImageField(
        upload_to=service_image_upload_path,
        blank=True,
        null=True,
        validators=[validate_image_file],
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "servicio"
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"

    def __str__(self):
        return self.nombre