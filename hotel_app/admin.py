from django.contrib import admin

from hotel_app.models import (
    Hotel,
    DireccionHotel,
    TipoHabitacion,
    Habitacion,
    Cama,
    TipoHabitacionCama,
    ImagenHabitacion,
    Servicio,
)


admin.site.register(Hotel)
admin.site.register(DireccionHotel)
admin.site.register(TipoHabitacion)
admin.site.register(Habitacion)
admin.site.register(Cama)
admin.site.register(TipoHabitacionCama)
admin.site.register(ImagenHabitacion)
admin.site.register(Servicio)