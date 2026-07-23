from datetime import date, timedelta

from rest_framework import serializers

from hotel_app.models import Reserva
from hotel_app.serializers.huesped_reserva import (
    HuespedReservaSerializer,
)
from hotel_app.serializers.reserva_habitacion import (
    ReservaHabitacionSerializer,
)
from hotel_app.serializers.reserva_servicio import (
    ReservaServicioSerializer,
)

MAX_STAY_NIGHTS = 30
MAX_ADVANCE_DAYS = 365


class RoomAssignmentInputSerializer(
    serializers.Serializer,
):
    habitacion_id = serializers.IntegerField(
        min_value=1,
    )
    cantidad_adultos = serializers.IntegerField(
        min_value=1,
    )
    cantidad_ninos = serializers.IntegerField(
        min_value=0,
    )


class GuestInputSerializer(
    serializers.Serializer,
):
    habitacion_id = serializers.IntegerField(
        min_value=1,
    )
    tipo_huesped = serializers.ChoiceField(
        choices=[
            'adulto',
            'nino',
        ],
    )
    nombres = serializers.CharField(
        max_length=100,
        trim_whitespace=True,
    )
    apellidos = serializers.CharField(
        max_length=100,
        trim_whitespace=True,
    )
    tipo_documento = serializers.CharField(
        max_length=30,
        trim_whitespace=True,
    )
    numero_documento = serializers.CharField(
        max_length=30,
        trim_whitespace=True,
    )
    edad = serializers.IntegerField(
        min_value=0,
        max_value=120,
    )
    telefono = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
        allow_null=True,
        trim_whitespace=True,
    )
    es_titular = serializers.BooleanField(
        default=False,
    )


class ServiceInputSerializer(
    serializers.Serializer,
):
    servicio_id = serializers.IntegerField(
        min_value=1,
    )
    cantidad = serializers.IntegerField(
        min_value=1,
        default=1,
    )


class CancelReservationInputSerializer(
    serializers.Serializer,
):
    motivo = serializers.CharField(
        max_length=1000,
        trim_whitespace=True,
    )

    def validate_motivo(self, value):
        if not value:
            raise serializers.ValidationError(
                'Indica el motivo de la cancelación.'
            )
        return value


class CompleteReservationInputSerializer(
    serializers.Serializer,
):
    fecha_entrada = serializers.DateField()
    fecha_salida = serializers.DateField()
    habitaciones = RoomAssignmentInputSerializer(
        many=True,
        allow_empty=False,
        max_length=10,
    )
    huespedes = GuestInputSerializer(
        many=True,
        allow_empty=False,
        max_length=50,
    )
    servicios = ServiceInputSerializer(
        many=True,
        required=False,
        allow_empty=True,
        default=list,
    )
    observaciones = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        default='',
        max_length=1000,
        trim_whitespace=True,
    )

    def validate(self, attrs):
        today = date.today()
        check_in = attrs['fecha_entrada']
        check_out = attrs['fecha_salida']

        if check_in < today:
            raise serializers.ValidationError({
                'fecha_entrada': (
                    'La fecha de entrada no puede ser pasada.'
                ),
            })

        maximum_check_in = today + timedelta(days=MAX_ADVANCE_DAYS)
        if check_in > maximum_check_in:
            raise serializers.ValidationError({
                'fecha_entrada': (
                    'La reserva puede realizarse con máximo un año de anticipación.'
                ),
            })

        if check_out <= check_in:
            raise serializers.ValidationError({
                'fecha_salida': (
                    'La fecha de salida debe ser mayor que la de entrada.'
                ),
            })

        nights = (check_out - check_in).days
        if nights > MAX_STAY_NIGHTS:
            raise serializers.ValidationError({
                'fecha_salida': (
                    'La estancia máxima permitida es de 30 noches.'
                ),
            })

        attrs['observaciones'] = attrs.get('observaciones') or ''
        return attrs


class ReservaSerializer(
    serializers.ModelSerializer,
):
    cliente_nombre = serializers.SerializerMethodField()
    cancelada_por_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Reserva
        fields = [
            'id',
            'codigo',
            'cliente',
            'cliente_nombre',
            'fecha_entrada',
            'fecha_salida',
            'numero_noches',
            'cantidad_adultos',
            'cantidad_ninos',
            'estado',
            'subtotal_habitaciones',
            'subtotal_servicios',
            'subtotal',
            'impuestos',
            'descuento',
            'total',
            'moneda',
            'observaciones',
            'motivo_cancelacion',
            'fecha_cancelacion',
            'cancelada_por',
            'cancelada_por_nombre',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

    def get_cliente_nombre(self, obj) -> str:
        return f'{obj.cliente.nombres} {obj.cliente.apellidos}'.strip()

    def get_cancelada_por_nombre(self, obj):
        if obj.cancelada_por is None:
            return None

        return (
            obj.cancelada_por.get_full_name().strip()
            or obj.cancelada_por.get_username()
        )


class ReservaDetailSerializer(
    ReservaSerializer,
):
    habitaciones_reservadas = ReservaHabitacionSerializer(
        many=True,
        read_only=True,
    )
    huespedes = HuespedReservaSerializer(
        many=True,
        read_only=True,
    )
    servicios = ReservaServicioSerializer(
        many=True,
        read_only=True,
    )

    class Meta(ReservaSerializer.Meta):
        fields = [
            *ReservaSerializer.Meta.fields,
            'habitaciones_reservadas',
            'huespedes',
            'servicios',
        ]
        read_only_fields = fields