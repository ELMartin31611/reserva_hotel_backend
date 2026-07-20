from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
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
        related_name='habitaciones_reservadas',
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
    cantidad_adultos = models.PositiveIntegerField(
        default=1,
    )
    cantidad_ninos = models.PositiveIntegerField(
        default=0,
    )
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
        verbose_name = 'Habitación reservada'
        verbose_name_plural = (
            'Habitaciones reservadas'
        )
        unique_together = (
            'reserva',
            'habitacion',
        )
        ordering = ['id']

    def clean(self):
        if (
            not self.reserva_id
            or not self.habitacion_id
        ):
            return

        existe_cruce = (
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

        if existe_cruce:
            raise ValidationError(
                'La habitación ya está reservada '
                'en ese rango de fechas.',
            )

    def __str__(self):
        return (
            f'{self.reserva.codigo} - '
            f'{self.habitacion}'
        )