from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hotel_app', '0009_reservation_cancellation_and_room_categories'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='mediahotel',
            name='media_hotel_hotel_i_6ce1ad_idx',
        ),
    ]
