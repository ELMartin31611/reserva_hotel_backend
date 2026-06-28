import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator


class Pago(models.Model):
    METODO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
    ]

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]

    reserva = models.ForeignKey(
        'hotel_app.Reserva',
        on_delete=models.CASCADE,
        related_name='pagos'
    )
    codigo_transaccion = models.CharField(
        max_length=80,
        unique=True,
        blank=True
    )
    metodo_pago = models.CharField(max_length=30, choices=METODO_CHOICES)
    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    estado = models.CharField(
        max_length=30,
        choices=ESTADO_CHOICES,
        default='pendiente'
    )
    fecha_pago = models.DateTimeField(null=True, blank=True)
    referencia = models.CharField(max_length=120, blank=True, null=True)
    comprobante_url = models.CharField(max_length=255, blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'
        ordering = ['-created_at']

    def clean(self):
        if self.reserva and self.reserva.estado == 'cancelada':
            raise ValidationError(
                'No se puede pagar una reserva cancelada.'
            )

    def save(self, *args, **kwargs):
        if not self.codigo_transaccion:
            self.codigo_transaccion = f'PAY-{uuid.uuid4().hex[:10].upper()}'

        super().save(*args, **kwargs)

    def __str__(self):
        return self.codigo_transaccion