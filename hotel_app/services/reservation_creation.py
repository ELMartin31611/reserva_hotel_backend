from collections import Counter
from datetime import date, timedelta
from decimal import Decimal

from django.db import transaction
from rest_framework import serializers

from hotel_app.models import (
    Cliente,
    Habitacion,
    HuespedReserva,
    Reserva,
    ReservaHabitacion,
    ReservaServicio,
    TarifaHabitacion,
)
from hotel_app.services.pricing_calculator import (
    PricingCalculator,
    money,
)

MAX_STAY_NIGHTS = 30
MAX_ADVANCE_DAYS = 365

NON_BOOKABLE_ROOM_STATES = {
    'mantenimiento',
    'inactiva',
    'inactivo',
    'ocupada',
    'ocupado',
    'bloqueada',
    'bloqueado',
    'fuera de servicio',
    'fuera_servicio',
    'eliminada',
    'eliminado',
}


class ReservationCreationService:
    @transaction.atomic
    def create(
        self,
        *,
        user,
        validated_data,
    ):
        cliente = (
            Cliente.objects.select_related(
                'perfil',
                'perfil__user',
            )
            .filter(
                perfil__user=user,
            )
            .order_by('id')
            .first()
        )

        if cliente is None:
            raise serializers.ValidationError({
                'cliente': (
                    'Completa tus datos de cliente '
                    'antes de reservar.'
                ),
            })

        fecha_entrada = validated_data['fecha_entrada']
        fecha_salida = validated_data['fecha_salida']
        assignments = validated_data['habitaciones']
        guests = validated_data['huespedes']
        services_input = validated_data.get('servicios', [])

        today = date.today()
        if fecha_entrada < today:
            raise serializers.ValidationError({
                'fecha_entrada': 'La fecha de entrada no puede ser pasada.'
            })

        if fecha_entrada > today + timedelta(days=MAX_ADVANCE_DAYS):
            raise serializers.ValidationError({
                'fecha_entrada': (
                    'La reserva puede realizarse con '
                    'máximo un año de anticipación.'
                )
            })

        nights = (fecha_salida - fecha_entrada).days

        if nights < 1 or nights > MAX_STAY_NIGHTS:
            raise serializers.ValidationError({
                'fecha_salida': (
                    'La estancia debe tener entre '
                    f'1 y {MAX_STAY_NIGHTS} noches.'
                ),
            })

        room_ids = [item['habitacion_id'] for item in assignments]

        if len(room_ids) != len(set(room_ids)):
            raise serializers.ValidationError({
                'habitaciones': (
                    'Una habitación física '
                    'no puede repetirse.'
                ),
            })

        # Lock rooms for update to prevent race conditions
        rooms = (
            Habitacion.objects
            .select_for_update()
            .select_related(
                'hotel',
                'tipo_habitacion',
            )
            .filter(id__in=room_ids)
            .order_by('id')
        )

        rooms_by_id = {room.id: room for room in rooms}

        missing_rooms = set(room_ids) - set(rooms_by_id)
        if missing_rooms:
            raise serializers.ValidationError({
                'habitaciones': 'Una o más habitaciones no existen.',
            })

        hotel_ids = {room.hotel_id for room in rooms_by_id.values()}
        if len(hotel_ids) != 1:
            raise serializers.ValidationError({
                'habitaciones': (
                    'Todas las habitaciones deben '
                    'pertenecer al mismo hotel.'
                ),
            })

        adults_total = 0
        children_total = 0
        expected_guests_by_room = {}

        for assignment in assignments:
            room = rooms_by_id[assignment['habitacion_id']]
            adults = assignment['cantidad_adultos']
            children = assignment['cantidad_ninos']
            total_guests = adults + children
            room_type = room.tipo_habitacion

            room_state = room.estado.strip().lower()
            if room_state in NON_BOOKABLE_ROOM_STATES:
                raise serializers.ValidationError({
                    'habitaciones': (
                        f'La habitación {room.numero} '
                        'no está disponible.'
                    ),
                })

            if adults < 1:
                raise serializers.ValidationError({
                    'habitaciones': (
                        f'La habitación {room.numero} '
                        'debe tener al menos un adulto.'
                    ),
                })

            if children > 0 and room_type.capacidad_ninos <= 0:
                raise serializers.ValidationError({
                    'habitaciones': (
                        f'La habitación {room.numero} '
                        'no permite niños.'
                    ),
                })

            maximum_guests = room_type.capacidad_maxima
            if total_guests > maximum_guests:
                raise serializers.ValidationError({
                    'habitaciones': (
                        f'La habitación {room.numero} '
                        f'admite máximo {maximum_guests} huésped(es): '
                        f'{room_type.capacidad_total} incluidos y '
                        f'{room_type.capacidad_extra} extra.'
                    ),
                })

            adults_total += adults
            children_total += children

            expected_guests_by_room[room.id] = {
                'adulto': adults,
                'nino': children,
            }

        # Check overlapping active/confirmed reservations
        occupied_room_ids = set(
            ReservaHabitacion.objects.filter(
                habitacion_id__in=room_ids,
                reserva__estado__in=['pendiente', 'confirmada'],
                reserva__fecha_entrada__lt=fecha_salida,
                reserva__fecha_salida__gt=fecha_entrada,
            ).values_list('habitacion_id', flat=True)
        )

        if occupied_room_ids:
            occupied_numbers = [
                rooms_by_id[room_id].numero
                for room_id in occupied_room_ids
            ]
            raise serializers.ValidationError({
                'disponibilidad': (
                    'Ya no están disponibles las habitaciones: '
                    f'{", ".join(occupied_numbers)}.'
                ),
            })

        self._validate_guests(
            guests=guests,
            room_ids=set(room_ids),
            expected_by_room=expected_guests_by_room,
        )

        room_type_ids = {
            room.tipo_habitacion_id
            for room in rooms_by_id.values()
        }

        rates = (
            TarifaHabitacion.objects
            .select_related(
                'temporada',
                'tipo_habitacion',
            )
            .filter(
                tipo_habitacion_id__in=room_type_ids,
                is_active=True,
                temporada__is_active=True,
                temporada__fecha_inicio__lt=fecha_salida,
                temporada__fecha_fin__gt=fecha_entrada,
            )
            .order_by(
                '-temporada__porcentaje_incremento',
                '-id',
            )
        )

        rates_by_type = {}
        for rate in rates:
            rates_by_type.setdefault(
                rate.tipo_habitacion_id,
                [],
            ).append(rate)

        priced_assignments = []
        currencies = set()

        for assignment in assignments:
            room = rooms_by_id[assignment['habitacion_id']]
            pricing = PricingCalculator.calculate_room_pricing(
                room=room,
                adults=assignment['cantidad_adultos'],
                children=assignment['cantidad_ninos'],
                check_in=fecha_entrada,
                nights=nights,
                rates=rates_by_type.get(room.tipo_habitacion_id, []),
            )
            currencies.add(pricing['currency'])
            priced_assignments.append({
                'assignment': assignment,
                'room': room,
                **pricing,
            })

        if len(currencies) != 1:
            raise serializers.ValidationError({
                'moneda': (
                    'Todas las habitaciones deben '
                    'usar la misma moneda.'
                ),
            })

        currency = currencies.pop()

        # Calculate rooms subtotal (base + extra guest surcharges)
        subtotal_habitaciones = money(
            sum(
                (item['room_total_subtotal'] for item in priced_assignments),
                Decimal('0.00'),
            )
        )

        # Calculate services subtotal
        charged_services, subtotal_servicios = PricingCalculator.calculate_services(
            services_input=services_input,
            room_type_ids=room_type_ids,
            currency=currency,
        )

        # Calculate totals
        totals = PricingCalculator.calculate_totals(
            subtotal_habitaciones=subtotal_habitaciones,
            subtotal_servicios=subtotal_servicios,
            descuento=Decimal('0.00'),
        )

        reservation = Reserva.objects.create(
            cliente=cliente,
            fecha_entrada=fecha_entrada,
            fecha_salida=fecha_salida,
            numero_noches=nights,
            cantidad_adultos=adults_total,
            cantidad_ninos=children_total,
            estado='pendiente',
            subtotal_habitaciones=totals['subtotal_habitaciones'],
            subtotal_servicios=totals['subtotal_servicios'],
            subtotal=totals['subtotal'],
            impuestos=totals['impuestos'],
            descuento=totals['descuento'],
            total=totals['total'],
            moneda=currency,
            observaciones=validated_data.get('observaciones', ''),
        )

        reservation_rooms = []
        for item in priced_assignments:
            reservation_rooms.append(
                ReservaHabitacion.objects.create(
                    reserva=reservation,
                    habitacion=item['room'],
                    tarifa=item['first_rate'],
                    precio_noche=item['average_rate'],
                    noches=nights,
                    cantidad_adultos=item['assignment']['cantidad_adultos'],
                    cantidad_ninos=item['assignment']['cantidad_ninos'],
                    cantidad_huespedes_incluidos=item['included_guests'],
                    cantidad_huespedes_extra=item['extra_guests'],
                    subtotal_habitacion=item['room_base_subtotal'],
                    subtotal_huespedes_extra=item['extra_guests_subtotal'],
                    subtotal_adultos=Decimal('0.00'),
                    subtotal_ninos=Decimal('0.00'),
                    subtotal=item['room_total_subtotal'],
                    detalle_tarifas=item['breakdown'],
                    moneda=item['currency'],
                    estado='activa',
                )
            )

        reservation_room_by_physical_id = {
            item.habitacion_id: item
            for item in reservation_rooms
        }

        HuespedReserva.objects.bulk_create([
            HuespedReserva(
                reserva=reservation,
                reserva_habitacion=reservation_room_by_physical_id[guest['habitacion_id']],
                tipo_huesped=guest['tipo_huesped'],
                nombres=guest['nombres'].strip(),
                apellidos=guest['apellidos'].strip(),
                tipo_documento=guest['tipo_documento'],
                numero_documento=guest['numero_documento'].strip(),
                edad=guest['edad'],
                telefono=guest.get('telefono') or None,
                es_titular=guest.get('es_titular', False),
            )
            for guest in guests
        ])

        if charged_services:
            ReservaServicio.objects.bulk_create([
                ReservaServicio(
                    reserva=reservation,
                    servicio=cs['servicio'],
                    nombre=cs['nombre'],
                    cantidad=cs['cantidad'],
                    precio_unitario=cs['precio_unitario'],
                    subtotal=cs['subtotal'],
                    moneda=cs['moneda'],
                )
                for cs in charged_services
            ])

        return reservation

    def _validate_guests(
        self,
        *,
        guests,
        room_ids,
        expected_by_room,
    ):
        if not guests:
            raise serializers.ValidationError({
                'huespedes': 'Debes registrar los huéspedes seleccionados.',
            })

        document_numbers = [
            guest['numero_documento'].strip().upper()
            for guest in guests
        ]

        if len(document_numbers) != len(set(document_numbers)):
            raise serializers.ValidationError({
                'huespedes': 'No se puede repetir el documento de un huésped.',
            })

        actual_by_room = {room_id: Counter() for room_id in room_ids}
        holder_count = 0

        for guest in guests:
            room_id = guest['habitacion_id']
            guest_type = guest['tipo_huesped']
            age = guest['edad']

            if room_id not in room_ids:
                raise serializers.ValidationError({
                    'huespedes': (
                        'Un huésped está asignado a una '
                        'habitación no seleccionada.'
                    ),
                })

            if guest_type == 'adulto' and age < 18:
                raise serializers.ValidationError({
                    'huespedes': (
                        'Los huéspedes adultos deben '
                        'tener 18 años o más.'
                    ),
                })

            if guest_type == 'nino' and age >= 18:
                raise serializers.ValidationError({
                    'huespedes': (
                        'Los huéspedes niños deben ser '
                        'menores de 18 años.'
                    ),
                })

            if guest.get('es_titular'):
                holder_count += 1
                if guest_type != 'adulto':
                    raise serializers.ValidationError({
                        'huespedes': (
                            'El titular de la reserva '
                            'debe ser adulto.'
                        ),
                    })

            actual_by_room[room_id][guest_type] += 1

        if holder_count != 1:
            raise serializers.ValidationError({
                'huespedes': 'Debe existir exactamente un titular adulto.',
            })

        for room_id, expected in expected_by_room.items():
            actual = actual_by_room[room_id]
            if (
                actual['adulto'] != expected['adulto']
                or actual['nino'] != expected['nino']
            ):
                raise serializers.ValidationError({
                    'huespedes': (
                        'La cantidad de huéspedes registrados '
                        'no coincide con la selección de cada habitación.'
                    ),
                })