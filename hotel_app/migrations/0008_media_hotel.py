# Generated manually because the local database connection is unavailable.

import django.db.models.deletion
from django.db import migrations, models

import hotel_app.models.media_hotel
import hotel_app.validators


class Migration(migrations.Migration):

    dependencies = [
        ('hotel_app', '0007_factura_detalle_lineas_reserva_subtotal_habitaciones_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='MediaHotel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('imagen', 'Imagen'), ('video', 'Video')], max_length=10)),
                ('archivo', models.FileField(max_length=255, upload_to=hotel_app.models.media_hotel.hotel_media_upload_path, validators=[hotel_app.validators.validate_hotel_media_file])),
                ('titulo', models.CharField(max_length=100)),
                ('descripcion', models.TextField(blank=True, default='')),
                ('orden', models.PositiveIntegerField(default=0)),
                ('es_principal', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('hotel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='media', to='hotel_app.hotel')),
            ],
            options={
                'verbose_name': 'Media de hotel',
                'verbose_name_plural': 'Media de hoteles',
                'db_table': 'media_hotel',
                'ordering': ['orden', 'id'],
            },
        ),
        migrations.AddIndex(
            model_name='mediahotel',
            index=models.Index(fields=['hotel', 'tipo', 'orden'], name='media_hotel_hotel_i_6ce1ad_idx'),
        ),
    ]
