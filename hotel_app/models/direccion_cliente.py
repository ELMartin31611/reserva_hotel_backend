from django.db import models

from .cliente import Cliente


class DireccionCliente(models.Model):

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='direcciones'
    )

    provincia = models.CharField(
        max_length=100
    )

    ciudad = models.CharField(
        max_length=100
    )

    calle_principal = models.CharField(
        max_length=150
    )

    calle_secundaria = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    referencia = models.TextField(
        blank=True,
        null=True
    )

    codigo_postal = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    es_principal = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.ciudad} - {self.provincia}"

    class Meta:
        db_table = 'direccion_cliente'