from datetime import date, timedelta

from rest_framework import serializers

from hotel_app.models import Habitacion
from hotel_app.serializers.tipo_habitacion_servicio import TipoHabitacionServicioSerializer


class HabitacionSerializer(
    serializers.ModelSerializer
):
    hotel_nombre = serializers.CharField(
        source='hotel.nombre',
        read_only=True,
    )
    tipo_habitacion_nombre = serializers.CharField(
        source='tipo_habitacion.nombre',
        read_only=True,
    )
    capacidad_adultos = serializers.IntegerField(
        source='tipo_habitacion.capacidad_adultos',
        read_only=True,
    )
    capacidad_ninos = serializers.IntegerField(
        source='tipo_habitacion.capacidad_ninos',
        read_only=True,
    )
    capacidad_total = serializers.IntegerField(
        source='tipo_habitacion.capacidad_total',
        read_only=True,
    )
    capacidad_extra = serializers.IntegerField(
        source='tipo_habitacion.capacidad_extra',
        read_only=True,
    )
    capacidad_maxima = serializers.IntegerField(
        source='tipo_habitacion.capacidad_maxima',
        read_only=True,
    )
    imagen_principal = serializers.SerializerMethodField(
        read_only=True,
    )
    servicios = serializers.SerializerMethodField(
        read_only=True,
    )
    tipo_habitacion_detalle = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = Habitacion
        fields = [
            'id',
            'hotel',
            'hotel_nombre',
            'tipo_habitacion',
            'tipo_habitacion_nombre',
            'tipo_habitacion_detalle',
            'capacidad_adultos',
            'capacidad_ninos',
            'capacidad_total',
            'capacidad_extra',
            'capacidad_maxima',
            'imagen_principal',
            'servicios',
            'numero',
            'piso',
            'estado',
            'descripcion',
            'es_fumador',
            'observaciones',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'hotel_nombre',
            'tipo_habitacion_nombre',
            'tipo_habitacion_detalle',
            'capacidad_adultos',
            'capacidad_ninos',
            'capacidad_total',
            'capacidad_extra',
            'capacidad_maxima',
            'imagen_principal',
            'servicios',
            'created_at',
            'updated_at',
        ]

    def get_imagen_principal(self, obj):
        images = getattr(obj, 'imagenes_all', None)
        if images is None:
            images = list(obj.imagenes.all())

        if not images:
            return None

        principal = next((img for img in images if img.es_principal), images[0])
        if not principal.imagen_url:
            return None

        try:
            url = principal.imagen_url.url
        except ValueError:
            return None

        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(url)
        return url

    def get_servicios(self, obj):
        rts_qs = getattr(obj.tipo_habitacion, 'servicios_habitacion_all', None)
        if rts_qs is None:
            rts_qs = obj.tipo_habitacion.servicios_habitacion.all()

        return TipoHabitacionServicioSerializer(
            rts_qs,
            many=True,
            context=self.context,
        ).data

    def get_tipo_habitacion_detalle(self, obj):
        th = obj.tipo_habitacion
        return {
            'id': th.id,
            'nombre': th.nombre,
            'descripcion': th.descripcion,
            'capacidad_adultos': th.capacidad_adultos,
            'capacidad_ninos': th.capacidad_ninos,
            'capacidad_total': th.capacidad_total,
            'capacidad_extra': th.capacidad_extra,
            'capacidad_maxima': th.capacidad_maxima,
            'precio_base': str(th.precio_base),
            'tamano_m2': str(th.tamano_m2),
            'estado': th.estado,
        }

    def validate(self, attrs):
        hotel = attrs.get(
            'hotel',
            getattr(self.instance, 'hotel', None),
        )
        room_type = attrs.get(
            'tipo_habitacion',
            getattr(self.instance, 'tipo_habitacion', None),
        )
        number = attrs.get(
            'numero',
            getattr(self.instance, 'numero', ''),
        ).strip()

        if hotel and room_type and room_type.hotel_id != hotel.id:
            raise serializers.ValidationError({
                'tipo_habitacion': (
                    'El tipo de habitación no pertenece al hotel elegido.'
                ),
            })

        duplicates = Habitacion.objects.filter(
            hotel=hotel,
            numero__iexact=number,
        )

        if self.instance:
            duplicates = duplicates.exclude(pk=self.instance.pk)

        if hotel and number and duplicates.exists():
            raise serializers.ValidationError({
                'numero': 'Ya existe esa habitación en el hotel.',
            })

        attrs['numero'] = number
        return attrs


class AvailabilityQuerySerializer(serializers.Serializer):
    hotel = serializers.IntegerField(min_value=1)
    fecha_entrada = serializers.DateField(required=False)
    fecha_salida = serializers.DateField(required=False)
    entrada = serializers.DateField(required=False)
    salida = serializers.DateField(required=False)
    cantidad_adultos = serializers.IntegerField(min_value=1, required=False)
    adultos = serializers.IntegerField(min_value=1, required=False)
    cantidad_ninos = serializers.IntegerField(min_value=0, required=False)
    ninos = serializers.IntegerField(min_value=0, required=False)

    def to_internal_value(self, data):
        # Permitir aliases comunes como entrada, salida, adultos, ninos
        mutable_data = data.copy() if hasattr(data, 'copy') else dict(data)

        if 'entrada' in mutable_data and 'fecha_entrada' not in mutable_data:
            mutable_data['fecha_entrada'] = mutable_data['entrada']
        if 'salida' in mutable_data and 'fecha_salida' not in mutable_data:
            mutable_data['fecha_salida'] = mutable_data['salida']
        if 'adultos' in mutable_data and 'cantidad_adultos' not in mutable_data:
            mutable_data['cantidad_adultos'] = mutable_data['adultos']
        if 'ninos' in mutable_data and 'cantidad_ninos' not in mutable_data:
            mutable_data['cantidad_ninos'] = mutable_data['ninos']

        return super().to_internal_value(mutable_data)

    def validate(self, attrs):
        check_in = attrs.get('fecha_entrada')
        check_out = attrs.get('fecha_salida')
        adults = attrs.get('cantidad_adultos')
        children = attrs.get('cantidad_ninos')

        if not check_in:
            raise serializers.ValidationError({
                'fecha_entrada': 'La fecha de entrada es obligatoria.'
            })
        if not check_out:
            raise serializers.ValidationError({
                'fecha_salida': 'La fecha de salida es obligatoria.'
            })
        if adults is None:
            raise serializers.ValidationError({
                'cantidad_adultos': 'La cantidad de adultos es obligatoria.'
            })
        if children is None:
            raise serializers.ValidationError({
                'cantidad_ninos': 'La cantidad de niños es obligatoria.'
            })

        today = date.today()
        if check_in < today:
            raise serializers.ValidationError({
                'fecha_entrada': 'La fecha de entrada no puede ser pasada.'
            })

        if check_in > today + timedelta(days=365):
            raise serializers.ValidationError({
                'fecha_entrada': 'Se puede consultar disponibilidad con máximo 1 año de anticipación.'
            })

        if check_out <= check_in:
            raise serializers.ValidationError({
                'fecha_salida': 'La fecha de salida debe ser mayor que la de entrada.'
            })

        nights = (check_out - check_in).days
        if nights > 30:
            raise serializers.ValidationError({
                'fecha_salida': 'La estancia máxima es de 30 noches.'
            })

        return attrs