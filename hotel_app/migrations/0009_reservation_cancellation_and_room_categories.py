from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hotel_app', '0008_media_hotel'),
    ]

    operations = [
        migrations.AddField(
            model_name='reserva',
            name='motivo_cancelacion',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='reserva',
            name='fecha_cancelacion',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='reserva',
            name='cancelada_por',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='reservas_canceladas',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='tipohabitacion',
            name='categoria',
            field=models.CharField(
                blank=True,
                choices=[
                    ('individual', 'Individual'),
                    ('doble', 'Doble'),
                    ('suite', 'Suite'),
                    ('vip', 'VIP'),
                    ('premium', 'Premium'),
                    ('presidencial', 'Presidencial'),
                ],
                help_text=(
                    'Categoría normalizada. Los registros históricos sin '
                    'categoría se conservan hasta ser normalizados.'
                ),
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddConstraint(
            model_name='tipohabitacion',
            constraint=models.UniqueConstraint(
                condition=models.Q(categoria__isnull=False),
                fields=('hotel', 'categoria'),
                name='unique_room_category_per_hotel',
            ),
        ),
    ]
