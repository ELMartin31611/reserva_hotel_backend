from pathlib import Path
from uuid import uuid4

from django.contrib.auth.models import User
from django.db import models

from hotel_app.validators import validate_image_file


def profile_image_upload_path(instance, filename):
    extension = Path(filename).suffix.lower()
    user_id = instance.user_id or 'sin-usuario'
    unique_name = f'{uuid4().hex}{extension}'

    return (
        f'perfiles/'
        f'{user_id}/'
        f'{unique_name}'
    )


class PerfilUsuario(models.Model):
    ROLES = [
        ('ADMIN', 'Administrador'),
        ('USUARIO', 'Usuario'),
    ]

    ESTADOS = [
        ('ACTIVO', 'Activo'),
        ('INACTIVO', 'Inactivo'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil',
    )

    rol = models.CharField(
        max_length=20,
        choices=ROLES,
        default='USUARIO',
    )

    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )

    foto_url = models.ImageField(
        upload_to=profile_image_upload_path,
        max_length=255,
        validators=[validate_image_file],
        blank=True,
        null=True,
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='ACTIVO',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f'{self.user.username} - {self.rol}'

    class Meta:
        db_table = 'perfil_usuario'
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'