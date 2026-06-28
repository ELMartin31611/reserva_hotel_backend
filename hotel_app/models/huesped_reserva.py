from django.db import models


class HuespedReserva(models.Model):
    reserva = models.ForeignKey(
        'hotel_app.Reserva',
        on_delete=models.CASCADE,
        related_name='huespedes'
    )
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    tipo_documento = models.CharField(max_length=30)
    numero_documento = models.CharField(max_length=30)
    edad = models.PositiveIntegerField(null=True, blank=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    es_titular = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Huésped de reserva'
        verbose_name_plural = 'Huéspedes de reserva'
        ordering = ['id']

    def __str__(self):
        return f'{self.nombres} {self.apellidos}'