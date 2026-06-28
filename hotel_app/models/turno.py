from django.db import models


class Turno(models.Model):

    nombre = models.CharField(
        max_length=50
    )

    hora_inicio = models.TimeField()

    hora_fin = models.TimeField()

    descripcion = models.TextField(
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'turno'