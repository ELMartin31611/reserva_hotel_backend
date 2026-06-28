from django.db import models
from django.core.exceptions import ValidationError


class NotificacionSistema(models.Model):
    class TipoNotificacion(models.TextChoices):
        INFO = 'info', 'Información'
        PROMOCION = 'promocion', 'Promoción'
        MANTENIMIENTO = 'mantenimiento', 'Mantenimiento'
        ALERTA = 'alerta', 'Alerta'
        POLITICA = 'politica', 'Política'

    titulo = models.CharField(max_length=150)
    mensaje = models.TextField()
    tipo = models.CharField(
        max_length=20,
        choices=TipoNotificacion.choices,
        default=TipoNotificacion.INFO
    )

    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Notificación del Sistema'
        verbose_name_plural = 'Notificaciones del Sistema'
        ordering = ['-created_at']

    def clean(self):
        if self.fecha_fin and self.fecha_fin < self.fecha_inicio:
            raise ValidationError(
                'La fecha fin no puede ser menor que la fecha de inicio.'
            )

    def __str__(self):
        return f'{self.titulo} - {self.tipo}'