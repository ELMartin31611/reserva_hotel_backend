from decimal import Decimal

from django.core.validators import (
    MinValueValidator,
)
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            'hotel_app',
            '0004_reserva_huespedes_precios',
        ),
    ]

    operations = [
        migrations.AddField(
            model_name='tipohabitacion',
            name='capacidad_extra',
            field=models.PositiveIntegerField(
                default=0,
                help_text=(
                    'Cantidad máxima de huéspedes '
                    'adicionales permitidos con '
                    'recargo.'
                ),
            ),
        ),
        migrations.AddField(
            model_name='reservahabitacion',
            name=(
                'cantidad_huespedes_incluidos'
            ),
            field=models.PositiveIntegerField(
                default=0,
            ),
        ),
        migrations.AddField(
            model_name='reservahabitacion',
            name='cantidad_huespedes_extra',
            field=models.PositiveIntegerField(
                default=0,
            ),
        ),
        migrations.AddField(
            model_name='reservahabitacion',
            name='subtotal_habitacion',
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal('0.00'),
                max_digits=10,
                validators=[
                    MinValueValidator(0),
                ],
            ),
        ),
        migrations.AddField(
            model_name='reservahabitacion',
            name=(
                'subtotal_huespedes_extra'
            ),
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal('0.00'),
                max_digits=10,
                validators=[
                    MinValueValidator(0),
                ],
            ),
        ),
    ]