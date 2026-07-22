from django.db import transaction
from rest_framework import serializers

from hotel_app.models import MediaHotel


class MediaHotelSerializer(serializers.ModelSerializer):
    archivo = serializers.FileField(write_only=True)
    archivo_url = serializers.SerializerMethodField()
    hotel_nombre = serializers.CharField(
        source='hotel.nombre',
        read_only=True,
    )

    class Meta:
        model = MediaHotel
        fields = [
            'id',
            'hotel',
            'hotel_nombre',
            'tipo',
            'archivo',
            'archivo_url',
            'titulo',
            'descripcion',
            'orden',
            'es_principal',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'hotel_nombre',
            'archivo_url',
            'created_at',
            'updated_at',
        ]

    def get_archivo_url(self, obj):
        if not obj.archivo:
            return None
        request = self.context.get('request')
        url = obj.archivo.url
        return request.build_absolute_uri(url) if request else url

    def validate(self, attrs):
        media_type = attrs.get('tipo', getattr(self.instance, 'tipo', None))
        file_obj = attrs.get('archivo')
        if file_obj:
            is_video = file_obj.name.lower().endswith(('.mp4', '.webm'))
            if (media_type == 'video') != is_video:
                raise serializers.ValidationError({
                    'archivo': 'El tipo debe coincidir con el archivo enviado.',
                })
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        media = super().create(validated_data)
        self._clear_other_main(media)
        return media

    @transaction.atomic
    def update(self, instance, validated_data):
        media = super().update(instance, validated_data)
        self._clear_other_main(media)
        return media

    def _clear_other_main(self, media):
        if media.tipo == 'imagen' and media.es_principal:
            MediaHotel.objects.filter(
                hotel=media.hotel,
                tipo='imagen',
                es_principal=True,
            ).exclude(id=media.id).update(es_principal=False)
