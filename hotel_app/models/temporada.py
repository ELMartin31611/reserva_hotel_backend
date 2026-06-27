from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator


class Temporada(models.Model):
    nombre = models.CharField(max_length=80)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    porcentaje_incremento = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    descripcion = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Temporada'
        verbose_name_plural = 'Temporadas'
        ordering = ['fecha_inicio']

    def clean(self):
        if self.fecha_fin <= self.fecha_inicio:
            raise ValidationError(
                'La fecha fin debe ser mayor que la fecha de inicio.'
            )

    def __str__(self):
        return self.nombre
    