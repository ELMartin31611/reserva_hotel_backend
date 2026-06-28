from django.db import models

from .cliente import Cliente


class DocumentoCliente(models.Model):

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='documentos'
    )

    tipo_documento = models.CharField(
        max_length=30
    )

    numero_documento = models.CharField(
        max_length=30
    )

    archivo_url = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    fecha_emision = models.DateField(
        blank=True,
        null=True
    )

    fecha_expiracion = models.DateField(
        blank=True,
        null=True
    )

    verificado = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.tipo_documento} - {self.numero_documento}"

    class Meta:
        db_table = 'documento_cliente'