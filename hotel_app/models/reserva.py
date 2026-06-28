import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator


class Reserva(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('finalizada', 'Finalizada'),
    ]

    codigo = models.CharField(max_length=30, unique=True, blank=True)
    cliente = models.ForeignKey(
        'hotel_app.Cliente',
        on_delete=models.CASCADE,
        related_name='reservas'
    )
    fecha_entrada = models.DateField()
    fecha_salida = models.DateField()
    numero_noches = models.PositiveIntegerField(default=1)
    cantidad_adultos = models.PositiveIntegerField(default=1)
    cantidad_ninos = models.PositiveIntegerField(default=0)
    estado = models.CharField(
        max_length=30,
        choices=ESTADO_CHOICES,
        default='pendiente'
    )
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    impuestos = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    descuento = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    observaciones = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-created_at']

    def clean(self):
        if self.fecha_salida <= self.fecha_entrada:
            raise ValidationError(
                'La fecha de salida debe ser mayor que la fecha de entrada.'
            )

    def calcular_noches(self):
        return (self.fecha_salida - self.fecha_entrada).days

    def save(self, *args, **kwargs):
        if not self.codigo:
            self.codigo = f'RES-{uuid.uuid4().hex[:8].upper()}'

        if self.fecha_entrada and self.fecha_salida:
            self.numero_noches = self.calcular_noches()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.codigo