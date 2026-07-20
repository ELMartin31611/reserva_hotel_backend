import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            'hotel_app',
            '0003_hotel_logo_alter_hotel_logo_url_and_more',
        ),
    ]

    operations = [
        migrations.AddField(
            model_name='huespedreserva',
            name='reserva_habitacion',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=(
                    django.db.models.deletion.CASCADE
                ),
                related_name='huespedes',
                to='hotel_app.reservahabitacion',
            ),
        ),
        migrations.AddField(
            model_name='huespedreserva',
            name='tipo_huesped',
            field=models.CharField(
                choices=[
                    ('adulto', 'Adulto'),
                    ('nino', 'Niño'),
                ],
                default='adulto',
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name='reserva',
            name='moneda',
            field=models.CharField(
                default='USD',
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name='reservahabitacion',
            name='cantidad_adultos',
            field=models.PositiveIntegerField(
                default=1,
            ),
        ),
        migrations.AddField(
            model_name='reservahabitacion',
            name='cantidad_ninos',
            field=models.PositiveIntegerField(
                default=0,
            ),
        ),
        migrations.AddField(
            model_name='reservahabitacion',
            name='detalle_tarifas',
            field=models.JSONField(
                blank=True,
                default=list,
            ),
        ),
        migrations.AddField(
            model_name='reservahabitacion',
            name='moneda',
            field=models.CharField(
                default='USD',
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name='reservahabitacion',
            name='subtotal_adultos',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=10,
                validators=[
                    django.core.validators
                    .MinValueValidator(0),
                ],
            ),
        ),
        migrations.AddField(
            model_name='reservahabitacion',
            name='subtotal_ninos',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=10,
                validators=[
                    django.core.validators
                    .MinValueValidator(0),
                ],
            ),
        ),
    ]