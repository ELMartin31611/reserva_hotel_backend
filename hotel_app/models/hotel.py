from django.db import models


class Hotel(models.Model):
    nombre = models.CharField(max_length=150)
    ruc = models.CharField(max_length=20)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(max_length=254)
    descripcion = models.TextField()
    categoria_estrellas = models.IntegerField()
    sitio_web = models.URLField(max_length=255)
    logo_url = models.URLField(max_length=255)
    estado = models.CharField(max_length=20)
    hora_check_in = models.TimeField()
    hora_check_out = models.TimeField()
    permite_mascotas = models.BooleanField(default=False)
    edad_minima_reserva = models.IntegerField()
    politica_cancelacion = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "hotel"
        verbose_name = "Hotel"
        verbose_name_plural = "Hoteles"

    def __str__(self):
        return self.nombre