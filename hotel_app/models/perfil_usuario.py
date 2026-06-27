from django.db import models
from django.contrib.auth.models import User


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
        related_name='perfil'
    )

    rol = models.CharField(
        max_length=20,
        choices=ROLES,
        default='USUARIO'
    )

    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    foto_url = models.URLField(
        max_length=255,
        blank=True,
        null=True
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default='ACTIVO'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.rol}"

    class Meta:
        db_table = 'perfil_usuario'
        verbose_name = 'Perfil de Usuario'
        verbose_name_plural = 'Perfiles de Usuario'