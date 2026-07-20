from collections import Counter
from datetime import timedelta
from decimal import (
    Decimal,
    ROUND_HALF_UP,
)

from django.db import transaction
from rest_framework import serializers

from hotel_app.models import (
    Cliente,
    Habitacion,
    HuespedReserva,
    Reserva,
    ReservaHabitacion,
    TarifaHabitacion,
)


MONEY_QUANTUM = Decimal('0.01')
EXTRA_GUEST_PRICE_FACTOR = Decimal('0.50')
TAX_RATE = Decimal('0.12')
MAX_STAY_NIGHTS = 30

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
}


def money(value):
    return Decimal(value).quantize(
        MONEY_QUANTUM,
        rounding=ROUND_HALF_UP,
    )


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

        fecha_entrada = (
            validated_data['fecha_entrada']
        )
        fecha_salida = (
            validated_data['fecha_salida']
        )
        assignments = (
            validated_data['habitaciones']
        )
        guests = validated_data['huespedes']

        nights = (
            fecha_salida - fecha_entrada
        ).days

        if (
            nights < 1
            or nights > MAX_STAY_NIGHTS
        ):
            raise serializers.ValidationError({
                'fecha_salida': (
                    'La estancia debe tener entre '
                    f'1 y {MAX_STAY_NIGHTS} noches.'
                ),
            })

        room_ids = [
            item['habitacion_id']
            for item in assignments
        ]

        if (
            len(room_ids)
            != len(set(room_ids))
        ):
            raise serializers.ValidationError({
                'habitaciones': (
                    'Una habitación física '
                    'no puede repetirse.'
                ),
            })

        rooms = (
            Habitacion.objects
            .select_for_update()
            .select_related(
                'hotel',
                'tipo_habitacion',
            )
            .filter(id__in=room_ids)
        )

        rooms_by_id = {
            room.id: room
            for room in rooms
        }

        missing_rooms = (
            set(room_ids)
            - set(rooms_by_id)
        )

        if missing_rooms:
            raise serializers.ValidationError({
                'habitaciones': (
                    'Una o más habitaciones '
                    'no existen.'
                ),
            })

        hotel_ids = {
            room.hotel_id
            for room in rooms_by_id.values()
        }

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
            room = rooms_by_id[
                assignment['habitacion_id']
            ]
            adults = assignment[
                'cantidad_adultos'
            ]
            children = assignment[
                'cantidad_ninos'
            ]
            total_guests = adults + children
            room_type = room.tipo_habitacion

            room_state = (
                room.estado
                .strip()
                .lower()
            )

            if (
                room_state
                in NON_BOOKABLE_ROOM_STATES
            ):
                raise serializers.ValidationError({
                    'habitaciones': (
                        f'La habitación {room.numero} '
                        'no está disponible.'
                    ),
                })

            if adults < 1:
                raise serializers.ValidationError({
                    'habitaciones': (
                        'Cada habitación debe tener '
                        'al menos un adulto.'
                    ),
                })

            if (
                children > 0
                and room_type.capacidad_ninos <= 0
            ):
                raise serializers.ValidationError({
                    'habitaciones': (
                        f'La habitación {room.numero} '
                        'no permite niños.'
                    ),
                })

            maximum_adults = (
                room_type.capacidad_adultos
                + room_type.capacidad_extra
            )
            maximum_children = (
                room_type.capacidad_ninos
                + room_type.capacidad_extra
            )
            maximum_guests = (
                room_type.capacidad_total
                + room_type.capacidad_extra
            )

            if adults > maximum_adults:
                raise serializers.ValidationError({
                    'habitaciones': (
                        f'La habitación {room.numero} '
                        f'admite máximo '
                        f'{maximum_adults} adulto(s).'
                    ),
                })

            if children > maximum_children:
                raise serializers.ValidationError({
                    'habitaciones': (
                        f'La habitación {room.numero} '
                        f'admite máximo '
                        f'{maximum_children} niño(s).'
                    ),
                })

            if total_guests > maximum_guests:
                raise serializers.ValidationError({
                    'habitaciones': (
                        f'La habitación {room.numero} '
                        f'admite máximo '
                        f'{maximum_guests} huésped(es): '
                        f'{room_type.capacidad_total} '
                        'incluidos y '
                        f'{room_type.capacidad_extra} '
                        'extra.'
                    ),
                })

            adults_total += adults
            children_total += children

            expected_guests_by_room[room.id] = {
                'adulto': adults,
                'nino': children,
            }

        occupied_room_ids = set(
            ReservaHabitacion.objects.filter(
                habitacion_id__in=room_ids,
                reserva__estado__in=[
                    'pendiente',
                    'confirmada',
                ],
                reserva__fecha_entrada__lt=(
                    fecha_salida
                ),
                reserva__fecha_salida__gt=(
                    fecha_entrada
                ),
            ).values_list(
                'habitacion_id',
                flat=True,
            )
        )

        if occupied_room_ids:
            occupied_numbers = [
                rooms_by_id[room_id].numero
                for room_id
                in occupied_room_ids
            ]

            raise serializers.ValidationError({
                'disponibilidad': (
                    'Ya no están disponibles '
                    'las habitaciones: '
                    f'{", ".join(occupied_numbers)}.'
                ),
            })

        self._validate_guests(
            guests=guests,
            room_ids=set(room_ids),
            expected_by_room=(
                expected_guests_by_room
            ),
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
                tipo_habitacion_id__in=(
                    room_type_ids
                ),
                is_active=True,
                temporada__is_active=True,
                temporada__fecha_inicio__lt=(
                    fecha_salida
                ),
                temporada__fecha_fin__gt=(
                    fecha_entrada
                ),
            )
            .order_by(
                '-temporada'
                '__porcentaje_incremento',
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
            room = rooms_by_id[
                assignment['habitacion_id']
            ]

            pricing = self._price_room(
                room=room,
                adults=assignment[
                    'cantidad_adultos'
                ],
                children=assignment[
                    'cantidad_ninos'
                ],
                check_in=fecha_entrada,
                nights=nights,
                rates=rates_by_type.get(
                    room.tipo_habitacion_id,
                    [],
                ),
            )

            currencies.add(
                pricing['currency']
            )

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

        room_base_subtotal = money(
            sum(
                (
                    item['room_subtotal']
                    for item
                    in priced_assignments
                ),
                Decimal('0.00'),
            )
        )
        extra_guests_subtotal = money(
            sum(
                (
                    item['extra_guests_subtotal']
                    for item
                    in priced_assignments
                ),
                Decimal('0.00'),
            )
        )
        subtotal = money(
            room_base_subtotal
            + extra_guests_subtotal
        )
        taxes = money(
            subtotal * TAX_RATE
        )
        total = money(
            subtotal + taxes
        )
        currency = currencies.pop()

        reservation = Reserva.objects.create(
            cliente=cliente,
            fecha_entrada=fecha_entrada,
            fecha_salida=fecha_salida,
            numero_noches=nights,
            cantidad_adultos=adults_total,
            cantidad_ninos=children_total,
            estado='pendiente',
            subtotal=subtotal,
            impuestos=taxes,
            descuento=Decimal('0.00'),
            total=total,
            moneda=currency,
            observaciones=(
                validated_data.get(
                    'observaciones',
                    '',
                )
            ),
        )

        reservation_rooms = []

        for item in priced_assignments:
            reservation_rooms.append(
                ReservaHabitacion.objects.create(
                    reserva=reservation,
                    habitacion=item['room'],
                    tarifa=item['first_rate'],
                    precio_noche=(
                        item['average_rate']
                    ),
                    noches=nights,
                    cantidad_adultos=(
                        item['assignment'][
                            'cantidad_adultos'
                        ]
                    ),
                    cantidad_ninos=(
                        item['assignment'][
                            'cantidad_ninos'
                        ]
                    ),
                    cantidad_huespedes_incluidos=(
                        item['included_guests']
                    ),
                    cantidad_huespedes_extra=(
                        item['extra_guests']
                    ),
                    subtotal_habitacion=(
                        item['room_subtotal']
                    ),
                    subtotal_huespedes_extra=(
                        item[
                            'extra_guests_subtotal'
                        ]
                    ),
                    subtotal_adultos=Decimal(
                        '0.00'
                    ),
                    subtotal_ninos=Decimal(
                        '0.00'
                    ),
                    subtotal=item['subtotal'],
                    detalle_tarifas=(
                        item['breakdown']
                    ),
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
                reserva_habitacion=(
                    reservation_room_by_physical_id[
                        guest['habitacion_id']
                    ]
                ),
                tipo_huesped=(
                    guest['tipo_huesped']
                ),
                nombres=(
                    guest['nombres'].strip()
                ),
                apellidos=(
                    guest['apellidos'].strip()
                ),
                tipo_documento=(
                    guest['tipo_documento']
                ),
                numero_documento=(
                    guest[
                        'numero_documento'
                    ].strip()
                ),
                edad=guest['edad'],
                telefono=(
                    guest.get('telefono')
                    or None
                ),
                es_titular=(
                    guest.get(
                        'es_titular',
                        False,
                    )
                ),
            )
            for guest in guests
        ])

        return reservation

    def _price_room(
        self,
        *,
        room,
        adults,
        children,
        check_in,
        nights,
        rates,
    ):
        room_subtotal = Decimal('0.00')
        extra_guests_subtotal = (
            Decimal('0.00')
        )
        breakdown = []
        first_rate = None
        currency = None

        total_guests = adults + children
        included_capacity = (
            room.tipo_habitacion
            .capacidad_total
        )
        included_guests = min(
            total_guests,
            included_capacity,
        )
        extra_guests = max(
            0,
            total_guests
            - included_capacity,
        )

        for offset in range(nights):
            current_date = (
                check_in
                + timedelta(days=offset)
            )

            rate = next(
                (
                    item
                    for item in rates
                    if (
                        item.temporada
                        .fecha_inicio
                        <= current_date
                        < item.temporada
                        .fecha_fin
                    )
                ),
                None,
            )

            if rate is None:
                raise serializers.ValidationError({
                    'tarifa': (
                        'No existe tarifa activa '
                        f'para la habitación '
                        f'{room.numero} el '
                        f'{current_date.isoformat()}.'
                    ),
                })

            nightly_room_price = (
                rate.precio_fin_semana
                if (
                    current_date.weekday() >= 5
                    and rate
                    .precio_fin_semana
                    is not None
                )
                else rate.precio_noche
            )
            nightly_room_price = money(
                nightly_room_price
            )

            if first_rate is None:
                first_rate = rate
                currency = rate.moneda
            elif rate.moneda != currency:
                raise serializers.ValidationError({
                    'moneda': (
                        'Las tarifas de la '
                        f'habitación {room.numero} '
                        'usan monedas diferentes.'
                    ),
                })

            extra_guest_unit_charge = money(
                nightly_room_price
                * EXTRA_GUEST_PRICE_FACTOR
            )
            nightly_extra_total = money(
                extra_guest_unit_charge
                * extra_guests
            )
            nightly_total = money(
                nightly_room_price
                + nightly_extra_total
            )

            room_subtotal += (
                nightly_room_price
            )
            extra_guests_subtotal += (
                nightly_extra_total
            )

            breakdown.append({
                'fecha': (
                    current_date.isoformat()
                ),
                'tarifa_id': rate.id,
                'temporada': (
                    rate.temporada.nombre
                ),
                'precio_habitacion': str(
                    nightly_room_price
                ),
                'huespedes_incluidos': (
                    included_guests
                ),
                'huespedes_extra': (
                    extra_guests
                ),
                'cargo_unitario_extra': str(
                    extra_guest_unit_charge
                ),
                'subtotal_huespedes_extra': str(
                    nightly_extra_total
                ),
                'total_noche': str(
                    nightly_total
                ),
                'moneda': rate.moneda,
            })

        room_subtotal = money(
            room_subtotal
        )
        extra_guests_subtotal = money(
            extra_guests_subtotal
        )
        subtotal = money(
            room_subtotal
            + extra_guests_subtotal
        )

        return {
            'first_rate': first_rate,
            'average_rate': money(
                room_subtotal / nights
            ),
            'included_guests': (
                included_guests
            ),
            'extra_guests': extra_guests,
            'room_subtotal': room_subtotal,
            'extra_guests_subtotal': (
                extra_guests_subtotal
            ),
            'subtotal': subtotal,
            'breakdown': breakdown,
            'currency': currency,
        }

    def _validate_guests(
        self,
        *,
        guests,
        room_ids,
        expected_by_room,
    ):
        if not guests:
            raise serializers.ValidationError({
                'huespedes': (
                    'Debes registrar los '
                    'huéspedes seleccionados.'
                ),
            })

        document_numbers = [
            guest['numero_documento']
            .strip()
            .upper()
            for guest in guests
        ]

        if (
            len(document_numbers)
            != len(set(document_numbers))
        ):
            raise serializers.ValidationError({
                'huespedes': (
                    'No se puede repetir el '
                    'documento de un huésped.'
                ),
            })

        actual_by_room = {
            room_id: Counter()
            for room_id in room_ids
        }
        holder_count = 0

        for guest in guests:
            room_id = guest['habitacion_id']
            guest_type = (
                guest['tipo_huesped']
            )
            age = guest['edad']

            if room_id not in room_ids:
                raise serializers.ValidationError({
                    'huespedes': (
                        'Un huésped está asignado '
                        'a una habitación no '
                        'seleccionada.'
                    ),
                })

            if (
                guest_type == 'adulto'
                and age < 18
            ):
                raise serializers.ValidationError({
                    'huespedes': (
                        'Los huéspedes adultos '
                        'deben tener 18 años o más.'
                    ),
                })

            if (
                guest_type == 'nino'
                and age >= 18
            ):
                raise serializers.ValidationError({
                    'huespedes': (
                        'Los huéspedes niños deben '
                        'ser menores de 18 años.'
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

            actual_by_room[
                room_id
            ][guest_type] += 1

        if holder_count != 1:
            raise serializers.ValidationError({
                'huespedes': (
                    'Debe existir exactamente '
                    'un titular adulto.'
                ),
            })

        for (
            room_id,
            expected,
        ) in expected_by_room.items():
            actual = actual_by_room[room_id]

            if (
                actual['adulto']
                != expected['adulto']
                or actual['nino']
                != expected['nino']
            ):
                raise serializers.ValidationError({
                    'huespedes': (
                        'La cantidad de huéspedes '
                        'registrados no coincide '
                        'con la selección de cada '
                        'habitación.'
                    ),
                })