from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

from rest_framework import serializers

from hotel_app.models import Servicio, TipoHabitacionServicio

MONEY_QUANTUM = Decimal('0.01')
EXTRA_GUEST_PRICE_FACTOR = Decimal('0.50')
TAX_RATE = Decimal('0.12')


def money(value):
    if value is None:
        return Decimal('0.00')
    return Decimal(str(value)).quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP)


class PricingCalculator:
    @staticmethod
    def calculate_room_pricing(*, room, adults, children, check_in, nights, rates):
        total_guests = adults + children
        room_type = room.tipo_habitacion

        if adults < 1:
            raise serializers.ValidationError({
                'habitaciones': f'La habitación {room.numero} debe contener al menos 1 adulto.'
            })

        if children > 0 and room_type.capacidad_ninos <= 0:
            raise serializers.ValidationError({
                'habitaciones': f'La habitación {room.numero} ({room_type.nombre}) no permite niños.'
            })

        capacity_included = room_type.capacidad_total
        capacity_extra = room_type.capacidad_extra
        capacity_max = room_type.capacidad_maxima

        if total_guests > capacity_max:
            raise serializers.ValidationError({
                'habitaciones': (
                    f'La habitación {room.numero} supera la capacidad máxima '
                    f'({capacity_max} huéspedes: {capacity_included} incluidos + {capacity_extra} extra).'
                )
            })

        extra_guests = max(0, total_guests - capacity_included)
        included_guests = min(total_guests, capacity_included)

        room_base_subtotal = Decimal('0.00')
        extra_guests_subtotal = Decimal('0.00')
        breakdown = []
        first_rate = None
        currency = 'USD'

        for offset in range(nights):
            current_date = check_in + timedelta(days=offset) if hasattr(check_in, 'day') else check_in

            matching_rates = [
                rate
                for rate in rates
                if (
                    rate.tipo_habitacion_id == room_type.id
                    and rate.is_active
                    and rate.temporada.is_active
                    and rate.temporada.fecha_inicio <= current_date < rate.temporada.fecha_fin
                )
            ]

            if not matching_rates:
                raise serializers.ValidationError({
                    'tarifa': (
                        f'No existe una tarifa activa para el tipo de habitación "{room_type.nombre}" '
                        f'en la fecha {current_date.isoformat()}.'
                    )
                })
            if len(matching_rates) > 1:
                raise serializers.ValidationError({
                    'tarifa': (
                        f'Existen tarifas activas superpuestas para el tipo de habitación '
                        f'"{room_type.nombre}" en la fecha {current_date.isoformat()}.'
                    )
                })

            matching_rate = matching_rates[0]

            if first_rate is None:
                first_rate = matching_rate
                currency = matching_rate.moneda
            elif matching_rate.moneda != currency:
                raise serializers.ValidationError({
                    'moneda': f'Las tarifas de la habitación {room.numero} difieren en la moneda.'
                })

            # Fin de semana: sábado (5) y domingo (6)
            is_weekend = current_date.weekday() >= 5
            if is_weekend and matching_rate.precio_fin_semana is not None:
                nightly_room_price = money(matching_rate.precio_fin_semana)
            else:
                nightly_room_price = money(matching_rate.precio_noche)

            recargo_unitario_extra = money(nightly_room_price * EXTRA_GUEST_PRICE_FACTOR)
            recargo_extra_noche = money(recargo_unitario_extra * extra_guests)
            total_noche = money(nightly_room_price + recargo_extra_noche)

            room_base_subtotal += nightly_room_price
            extra_guests_subtotal += recargo_extra_noche

            breakdown.append({
                'fecha': current_date.isoformat(),
                'tarifa_id': matching_rate.id,
                'temporada': matching_rate.temporada.nombre,
                'precio_habitacion': str(nightly_room_price),
                'huespedes_incluidos': included_guests,
                'huespedes_extra': extra_guests,
                'cargo_unitario_extra': str(recargo_unitario_extra),
                'subtotal_huespedes_extra': str(recargo_extra_noche),
                'total_noche': str(total_noche),
                'moneda': matching_rate.moneda,
            })

        room_base_subtotal = money(room_base_subtotal)
        extra_guests_subtotal = money(extra_guests_subtotal)
        room_total_subtotal = money(room_base_subtotal + extra_guests_subtotal)
        average_rate = money(room_base_subtotal / nights) if nights > 0 else Decimal('0.00')

        return {
            'first_rate': first_rate,
            'average_rate': average_rate,
            'included_guests': included_guests,
            'extra_guests': extra_guests,
            'room_base_subtotal': room_base_subtotal,
            'extra_guests_subtotal': extra_guests_subtotal,
            'room_total_subtotal': room_total_subtotal,
            'breakdown': breakdown,
            'currency': currency,
        }

    @staticmethod
    def calculate_services(*, services_input, room_type_ids, currency='USD'):
        if not services_input:
            return [], Decimal('0.00')

        service_ids = [s['servicio_id'] for s in services_input]
        if len(service_ids) != len(set(service_ids)):
            raise serializers.ValidationError({
                'servicios': 'No se permiten servicios repetidos en la selección; utiliza la cantidad.'
            })

        services = Servicio.objects.filter(id__in=service_ids)
        services_by_id = {s.id: s for s in services}

        missing_ids = set(service_ids) - set(services_by_id)
        if missing_ids:
            raise serializers.ValidationError({
                'servicios': 'Uno o más servicios seleccionados no existen.'
            })

        for s in services_by_id.values():
            if not s.is_active:
                raise serializers.ValidationError({
                    'servicios': f'El servicio "{s.nombre}" no está activo.'
                })

        room_type_services = TipoHabitacionServicio.objects.filter(
            servicio_id__in=service_ids,
            tipo_habitacion_id__in=room_type_ids,
        ).select_related('servicio')

        rts_by_service_id = {}
        for rts in room_type_services:
            rts_by_service_id.setdefault(rts.servicio_id, []).append(rts)

        charged_services = []
        subtotal_servicios = Decimal('0.00')

        for item in services_input:
            sid = item['servicio_id']
            qty = item.get('cantidad', 1)
            if qty < 1:
                raise serializers.ValidationError({
                    'servicios': 'La cantidad de un servicio debe ser al menos 1.'
                })

            service_obj = services_by_id[sid]
            rts_list = rts_by_service_id.get(sid, [])

            if not rts_list:
                raise serializers.ValidationError({
                    'servicios': (
                        f'El servicio "{service_obj.nombre}" no pertenece a ninguno de los '
                        'tipos de habitación seleccionados.'
                    )
                })

            # Si el servicio está incluido en alguno de los tipos reservados, no se cobra.
            is_included = any(rts.incluido for rts in rts_list)
            if is_included:
                continue

            # Si es adicional, buscar si tiene precio personalizado en alguno de los tipos de habitación
            custom_price = None
            for rts in rts_list:
                if rts.precio_personalizado is not None:
                    custom_price = rts.precio_personalizado
                    break

            unit_price = money(custom_price if custom_price is not None else service_obj.precio_extra)
            service_subtotal = money(unit_price * qty)

            charged_services.append({
                'servicio': service_obj,
                'nombre': service_obj.nombre,
                'cantidad': qty,
                'precio_unitario': unit_price,
                'subtotal': service_subtotal,
                'moneda': currency,
            })

            subtotal_servicios += service_subtotal

        subtotal_servicios = money(subtotal_servicios)
        return charged_services, subtotal_servicios

    @staticmethod
    def calculate_totals(*, subtotal_habitaciones, subtotal_servicios, descuento=Decimal('0.00')):
        subtotal_habitaciones = money(subtotal_habitaciones)
        subtotal_servicios = money(subtotal_servicios)
        descuento = money(descuento)

        subtotal = money(subtotal_habitaciones + subtotal_servicios)
        impuestos = money(subtotal * TAX_RATE)
        total = money(subtotal + impuestos - descuento)

        return {
            'subtotal_habitaciones': subtotal_habitaciones,
            'subtotal_servicios': subtotal_servicios,
            'subtotal': subtotal,
            'impuestos': impuestos,
            'descuento': descuento,
            'total': total,
        }
