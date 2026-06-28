from django.db import models
from django.contrib.auth.models import User

from .cargo_empleado import CargoEmpleado


class Empleado(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='empleados'
    )

    cargo = models.ForeignKey(
        CargoEmpleado,
        on_delete=models.CASCADE,
        related_name='empleados'
    )

    hotel_id = models.BigIntegerField()

    cedula = models.CharField(
        max_length=20,
        unique=True
    )

    nombres = models.CharField(
        max_length=100
    )

    apellidos = models.CharField(
        max_length=100
    )

    telefono = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    email = models.EmailField(
        blank=True,
        null=True
    )

    fecha_contratacion = models.DateField(
        blank=True,
        null=True
    )

    salario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    estado = models.CharField(
        max_length=20
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

    class Meta:
        db_table = 'empleado'