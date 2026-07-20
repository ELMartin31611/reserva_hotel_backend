from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            'hotel_app',
            '0005_precio_por_habitacion_y_capacidad_extra',
        ),
    ]

    operations = [
        migrations.AddField(
            model_name='pago',
            name='moneda',
            field=models.CharField(
                default='USD',
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name='factura',
            name='moneda',
            field=models.CharField(
                default='USD',
                max_length=10,
            ),
        ),
    ]