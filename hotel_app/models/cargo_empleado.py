from django.db import models


class CargoEmpleado(models.Model):

    nombre = models.CharField(
        max_length=80
    )

    descripcion = models.TextField(
        blank=True,
        null=True
    )

    nivel_acceso = models.IntegerField()

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
        db_table = 'cargo_empleado'