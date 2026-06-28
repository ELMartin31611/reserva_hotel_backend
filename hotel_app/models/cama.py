from django.db import models


class Cama(models.Model):
    nombre = models.CharField(max_length=80)
    capacidad_personas = models.IntegerField()
    descripcion = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "cama"
        verbose_name = "Cama"
        verbose_name_plural = "Camas"

    def __str__(self):
        return self.nombre