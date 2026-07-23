import hotel_app.models.servicio
import hotel_app.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotel_app', '0010_remove_mediahotel_media_hotel_hotel_i_6ce1ad_idx'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicio',
            name='imagen',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=hotel_app.models.servicio.service_image_upload_path,
                validators=[hotel_app.validators.validate_image_file],
            ),
        ),
    ]
