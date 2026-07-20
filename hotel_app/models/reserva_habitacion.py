from django.core.exceptions import (
    ValidationError,
)
from django.core.validators import (
    MinValueValidator,
)
from django.db import models


class ReservaHabitacion(models.Model):
    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('cancelada', 'Cancelada'),
        ('finalizada', 'Finalizada'),
    ]

    reserva = models.ForeignKey(
        'hotel_app.Reserva',
        on_delete=models.CASCADE,
        related_name=(
            'habitaciones_reservadas'
        ),
    )
    habitacion = models.ForeignKey(
        'hotel_app.Habitacion',
        on_delete=models.PROTECT,
        related_name='reservas_habitacion',
    )
    tarifa = models.ForeignKey(
        'hotel_app.TarifaHabitacion',
        on_delete=models.PROTECT,
        related_name='reservas_habitacion',
    )
    precio_noche = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
        ],
    )
    noches = models.PositiveIntegerField()
    cantidad_adultos = (
        models.PositiveIntegerField(
            default=1,
        )
    )
    cantidad_ninos = (
        models.PositiveIntegerField(
            default=0,
        )
    )

    cantidad_huespedes_incluidos = (
        models.PositiveIntegerField(
            default=0,
        )
    )
    cantidad_huespedes_extra = (
        models.PositiveIntegerField(
            default=0,
        )
    )

    subtotal_habitacion = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0),
        ],
    )
    subtotal_huespedes_extra = (
        models.DecimalField(
            max_digits=10,
            decimal_places=2,
            default=0,
            validators=[
                MinValueValidator(0),
            ],
        )
    )

    # Campos conservados para compatibilidad
    # con reservas creadas anteriormente.
    subtotal_adultos = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0),
        ],
    )
    subtotal_ninos = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
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
    estado = models.CharField(
        max_length=30,
        choices=ESTADO_CHOICES,
        default='activa',
    )
    detalle_tarifas = models.JSONField(
        default=list,
        blank=True,
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
        verbose_name = (
            'Habitación reservada'
        )
        verbose_name_plural = (
            'Habitaciones reservadas'
        )
        unique_together = (
            'reserva',
            'habitacion',
        )
        ordering = ['id']

    def clean(self):
        has_conflict = (
            ReservaHabitacion.objects.filter(
                habitacion=self.habitacion,
                reserva__estado__in=[
                    'pendiente',
                    'confirmada',
                ],
                reserva__fecha_entrada__lt=(
                    self.reserva.fecha_salida
                ),
                reserva__fecha_salida__gt=(
                    self.reserva.fecha_entrada
                ),
            )
            .exclude(id=self.id)
            .exists()
        )

        if has_conflict:
            raise ValidationError(
                'La habitación ya está '
                'reservada en ese rango de fechas.'
            )

    def __str__(self):
        return (
            f'{self.reserva.codigo} - '
            f'{self.habitacion}'
        )