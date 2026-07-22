from django.core.validators import MinValueValidator
from django.db import models


class ReservaServicio(models.Model):
    reserva = models.ForeignKey(
        'hotel_app.Reserva',
        on_delete=models.CASCADE,
        related_name='servicios',
    )
    servicio = models.ForeignKey(
        'hotel_app.Servicio',
        on_delete=models.PROTECT,
        related_name='reservas_servicio',
    )
    nombre = models.CharField(
        max_length=100,
    )
    cantidad = models.PositiveIntegerField(
        default=1,
    )
    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
        ],
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
        ],
    )
    moneda = models.CharField(
        max_length=10,
        default='USD',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        db_table = 'reserva_servicio'
        verbose_name = 'Servicio de reserva'
        verbose_name_plural = 'Servicios de reserva'
        unique_together = ('reserva', 'servicio')
        ordering = ['id']

    def __str__(self):
        return f'{self.reserva.codigo} - {self.nombre} (x{self.cantidad})'
