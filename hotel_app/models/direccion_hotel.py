from django.db import models

from hotel_app.models.hotel import Hotel


class DireccionHotel(models.Model):
    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        related_name="direcciones"
    )
    provincia = models.CharField(max_length=100)
    ciudad = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    referencia = models.TextField()
    latitud = models.DecimalField(max_digits=10, decimal_places=7)
    longitud = models.DecimalField(max_digits=10, decimal_places=7)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "direccion_hotel"
        verbose_name = "Dirección de Hotel"
        verbose_name_plural = "Direcciones de Hotel"

    def __str__(self):
        return f"{self.hotel.nombre} - {self.ciudad}"