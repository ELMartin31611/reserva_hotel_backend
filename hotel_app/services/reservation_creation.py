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
CHILD_PRICE_FACTOR = Decimal('0.50')
TAX_RATE = Decimal('0.12')
MAX_STAY_NIGHTS = 30

UNAVAILABLE_ROOM_STATES = {
    'mantenimiento',
    'en mantenimiento',
    'fuera de servicio',
    'inactiva',
    'inactivo',
    'bloqueada',
    'bloqueado',
    'no disponible',
}


def money(value):
    return Decimal(value).quantize(
        MONEY_QUANTUM,
        rounding=ROUND_HALF_UP,
    )


def normalize_room_state(
    value,
):
    return ' '.join(
        str(value)
        .strip()
        .lower()
        .replace('_', ' ')
        .replace('-', ' ')
        .split()
    )


class ReservationCreationService:
    @transaction.atomic
    def create(
        self,
        *,
        user,
        validated_data,
    ):
        customer = (
            Cliente.objects
            .select_related(
                'perfil',
                'perfil__user',
            )
            .filter(
                perfil__user=user,
            )
            .order_by('id')
            .first()
        )

        if customer is None:
            raise serializers.ValidationError({
                'cliente': (
                    'Completa tus datos de cliente '
                    'antes de reservar.'
                ),
            })

        check_in = validated_data[
            'fecha_entrada'
        ]
        check_out = validated_data[
            'fecha_salida'
        ]
        assignments = validated_data[
            'habitaciones'
        ]
        guests = validated_data[
            'huespedes'
        ]

        nights = (
            check_out
            - check_in
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
            assignment['habitacion_id']
            for assignment in assignments
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
            .filter(
                id__in=room_ids,
            )
            .order_by('id')
        )

        rooms_by_id = {
            room.id: room
            for room in rooms
        }

        missing_room_ids = (
            set(room_ids)
            - set(rooms_by_id)
        )

        if missing_room_ids:
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
            room_type = (
                room.tipo_habitacion
            )

            room_state = (
                normalize_room_state(
                    room.estado,
                )
            )

            if (
                room_state
                in UNAVAILABLE_ROOM_STATES
            ):
                raise serializers.ValidationError({
                    'habitaciones': (
                        f'La habitación {room.numero} '
                        'no está habilitada para reservas.'
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
                adults
                > room_type.capacidad_adultos
            ):
                raise serializers.ValidationError({
                    'habitaciones': (
                        f'La habitación {room.numero} '
                        'admite máximo '
                        f'{room_type.capacidad_adultos} '
                        'adulto(s).'
                    ),
                })

            if (
                children
                > room_type.capacidad_ninos
            ):
                raise serializers.ValidationError({
                    'habitaciones': (
                        f'La habitación {room.numero} '
                        'admite máximo '
                        f'{room_type.capacidad_ninos} '
                        'niño(s).'
                    ),
                })

            if (
                adults + children
                > room_type.capacidad_total
            ):
                raise serializers.ValidationError({
                    'habitaciones': (
                        'La capacidad total de la '
                        f'habitación {room.numero} es '
                        f'{room_type.capacidad_total}.'
                    ),
                })

            adults_total += adults
            children_total += children

            expected_guests_by_room[
                room.id
            ] = {
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
                    check_out
                ),
                reserva__fecha_salida__gt=(
                    check_in
                ),
            ).values_list(
                'habitacion_id',
                flat=True,
            )
        )

        if occupied_room_ids:
            occupied_numbers = [
                rooms_by_id[
                    room_id
                ].numero
                for room_id
                in occupied_room_ids
            ]

            raise serializers.ValidationError({
                'disponibilidad': (
                    'Ya no están disponibles las '
                    'habitaciones: '
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
            .select_for_update()
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
                    check_out
                ),
                temporada__fecha_fin__gt=(
                    check_in
                ),
            )
            .order_by(
                '-temporada__porcentaje_incremento',
                '-id',
            )
        )

        rates_by_room_type = {}

        for rate in rates:
            rates_by_room_type.setdefault(
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
                check_in=check_in,
                nights=nights,
                rates=(
                    rates_by_room_type.get(
                        room.tipo_habitacion_id,
                        [],
                    )
                ),
            )

            currencies.add(
                pricing['currency'],
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

        adults_subtotal = money(
            sum(
                (
                    item['adult_subtotal']
                    for item
                    in priced_assignments
                ),
                Decimal('0.00'),
            )
        )
        children_subtotal = money(
            sum(
                (
                    item['child_subtotal']
                    for item
                    in priced_assignments
                ),
                Decimal('0.00'),
            )
        )
        subtotal = money(
            adults_subtotal
            + children_subtotal
        )
        taxes = money(
            subtotal
            * TAX_RATE
        )
        total = money(
            subtotal
            + taxes
        )
        currency = currencies.pop()

        reservation = Reserva.objects.create(
            cliente=customer,
            fecha_entrada=check_in,
            fecha_salida=check_out,
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
            reservation_room = (
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
                    subtotal_adultos=(
                        item['adult_subtotal']
                    ),
                    subtotal_ninos=(
                        item['child_subtotal']
                    ),
                    subtotal=item['subtotal'],
                    detalle_tarifas=(
                        item['breakdown']
                    ),
                    moneda=item['currency'],
                    estado='activa',
                )
            )

            reservation_rooms.append(
                reservation_room,
            )

        reservation_room_by_id = {
            item.habitacion_id: item
            for item in reservation_rooms
        }

        HuespedReserva.objects.bulk_create([
            HuespedReserva(
                reserva=reservation,
                reserva_habitacion=(
                    reservation_room_by_id[
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
                    .strip()
                ),
                numero_documento=(
                    guest['numero_documento']
                    .strip()
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
        base_total = Decimal('0.00')
        breakdown = []
        first_rate = None
        currency = None

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
                        item.temporada.fecha_inicio
                        <= current_date
                        < item.temporada.fecha_fin
                    )
                ),
                None,
            )

            if rate is None:
                raise serializers.ValidationError({
                    'tarifa': (
                        'No existe tarifa activa para '
                        f'la habitación {room.numero} '
                        f'el {current_date.isoformat()}.'
                    ),
                })

            nightly_price = (
                rate.precio_fin_semana
                if (
                    current_date.weekday()
                    >= 5
                    and rate.precio_fin_semana
                    is not None
                )
                else rate.precio_noche
            )
            nightly_price = money(
                nightly_price,
            )

            if first_rate is None:
                first_rate = rate
                currency = rate.moneda
            elif rate.moneda != currency:
                raise serializers.ValidationError({
                    'moneda': (
                        'Las tarifas de la habitación '
                        f'{room.numero} usan monedas '
                        'diferentes.'
                    ),
                })

            base_total += nightly_price

            breakdown.append({
                'fecha': (
                    current_date.isoformat()
                ),
                'tarifa_id': rate.id,
                'temporada': (
                    rate.temporada.nombre
                ),
                'precio_noche': str(
                    nightly_price,
                ),
                'moneda': rate.moneda,
            })

        adult_subtotal = money(
            base_total
            * adults
        )
        child_subtotal = money(
            base_total
            * children
            * CHILD_PRICE_FACTOR
        )
        subtotal = money(
            adult_subtotal
            + child_subtotal
        )

        return {
            'first_rate': first_rate,
            'average_rate': money(
                base_total / nights,
            ),
            'adult_subtotal': (
                adult_subtotal
            ),
            'child_subtotal': (
                child_subtotal
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
                    'Debes registrar los huéspedes '
                    'seleccionados.'
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
                    'No se puede repetir el documento '
                    'de un huésped.'
                ),
            })

        actual_by_room = {
            room_id: Counter()
            for room_id in room_ids
        }
        holder_count = 0

        for guest in guests:
            room_id = guest[
                'habitacion_id'
            ]
            guest_type = guest[
                'tipo_huesped'
            ]
            age = guest['edad']

            if room_id not in room_ids:
                raise serializers.ValidationError({
                    'huespedes': (
                        'Un huésped está asignado a '
                        'una habitación no seleccionada.'
                    ),
                })

            if (
                guest_type == 'adulto'
                and age < 18
            ):
                raise serializers.ValidationError({
                    'huespedes': (
                        'Los huéspedes adultos deben '
                        'tener 18 años o más.'
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
                    'Debe existir exactamente un '
                    'titular adulto.'
                ),
            })

        for (
            room_id,
            expected,
        ) in expected_by_room.items():
            actual = actual_by_room[
                room_id
            ]

            if (
                actual['adulto']
                != expected['adulto']
                or actual['nino']
                != expected['nino']
            ):
                raise serializers.ValidationError({
                    'huespedes': (
                        'La cantidad de huéspedes '
                        'registrados no coincide con '
                        'la selección de cada habitación.'
                    ),
                })