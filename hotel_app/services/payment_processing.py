from django.db import transaction
from django.utils import timezone
from rest_framework import serializers

from hotel_app.models import (
    Factura,
    Pago,
    Reserva,
)
from hotel_app.permissions import (
    user_is_admin,
)


class PaymentProcessingService:
    @transaction.atomic
    def process(
        self,
        *,
        user,
        reservation_id,
        payment_method,
        reference='',
    ):
        reservation = (
            Reserva.objects
            .select_for_update()
            .select_related(
                'cliente',
                'cliente__perfil',
                'cliente__perfil__user',
            )
            .prefetch_related(
                'habitaciones_reservadas',
                'habitaciones_reservadas__habitacion',
                'habitaciones_reservadas__habitacion__tipo_habitacion',
                'servicios',
                'servicios__servicio',
            )
            .filter(pk=reservation_id)
            .first()
        )

        if reservation is None:
            raise serializers.ValidationError({
                'reserva_id': (
                    'La reserva no existe.'
                ),
            })

        is_admin = user_is_admin(user)

        owner_user_id = (
            reservation
            .cliente
            .perfil
            .user_id
        )

        if (
            not is_admin
            and owner_user_id != user.id
        ):
            raise serializers.ValidationError({
                'reserva_id': (
                    'No puedes pagar '
                    'una reserva ajena.'
                ),
            })

        if reservation.estado == 'cancelada':
            raise serializers.ValidationError({
                'estado': (
                    'No se puede pagar '
                    'una reserva cancelada.'
                ),
            })

        if reservation.estado != 'pendiente':
            raise serializers.ValidationError({
                'estado': (
                    'Solo se pueden pagar '
                    'reservas pendientes.'
                ),
            })

        if reservation.total <= 0:
            raise serializers.ValidationError({
                'total': (
                    'La reserva no tiene '
                    'un total válido.'
                ),
            })

        reference = reference.strip()

        if (
            payment_method == 'transferencia'
            and not reference
        ):
            raise serializers.ValidationError({
                'referencia': (
                    'La referencia es obligatoria '
                    'para transferencias.'
                ),
            })

        if (
            payment_method == 'efectivo'
            and not is_admin
        ):
            raise serializers.ValidationError({
                'metodo_pago': (
                    'Los pagos en efectivo solo '
                    'pueden registrarse desde '
                    'administración.'
                ),
            })

        has_approved_payment = (
            Pago.objects.filter(
                reserva=reservation,
                estado='aprobado',
            )
            .exists()
        )

        if has_approved_payment:
            raise serializers.ValidationError({
                'pago': (
                    'Esta reserva ya tiene '
                    'un pago aprobado.'
                ),
            })

        payment = Pago.objects.create(
            reserva=reservation,
            metodo_pago=payment_method,
            monto=reservation.total,
            moneda=reservation.moneda,
            estado='aprobado',
            fecha_pago=timezone.now(),
            referencia=reference or None,
            observaciones=(
                'Pago registrado exitosamente '
                'mediante StayBooking.'
            ),
        )

        reservation.estado = 'confirmada'
        reservation.save(
            update_fields=[
                'estado',
                'updated_at',
            ],
        )

        # Generar detalle de líneas para factura inmutable
        lineas_habitaciones = [
            {
                'habitacion_id': rh.habitacion_id,
                'habitacion_numero': rh.habitacion.numero,
                'tipo_habitacion': rh.habitacion.tipo_habitacion.nombre,
                'noches': rh.noches,
                'tarifa_por_noche': str(rh.precio_noche),
                'huespedes_incluidos': rh.cantidad_huespedes_incluidos,
                'huespedes_extra': rh.cantidad_huespedes_extra,
                'recargo_por_huesped_extra': [
                    {
                        'fecha': detalle['fecha'],
                        'precio_unitario': detalle['cargo_unitario_extra'],
                        'subtotal': detalle['subtotal_huespedes_extra'],
                    }
                    for detalle in rh.detalle_tarifas
                ],
                'subtotal_huespedes_extra': str(rh.subtotal_huespedes_extra),
                'subtotal_habitacion': str(rh.subtotal_habitacion),
                'subtotal': str(rh.subtotal),
                'detalle_tarifas_diarias': rh.detalle_tarifas,
            }
            for rh in reservation.habitaciones_reservadas.all()
        ]

        lineas_servicios = [
            {
                'servicio_id': rs.servicio_id,
                'nombre': rs.nombre,
                'cantidad': rs.cantidad,
                'precio_unitario': str(rs.precio_unitario),
                'subtotal': str(rs.subtotal),
                'moneda': rs.moneda,
            }
            for rs in reservation.servicios.all()
        ]

        detalle_lineas = {
            'habitaciones': lineas_habitaciones,
            'servicios_adicionales': lineas_servicios,
            'subtotal_habitaciones': str(reservation.subtotal_habitaciones),
            'subtotal_servicios': str(reservation.subtotal_servicios),
            'subtotal': str(reservation.subtotal),
            'impuestos': str(reservation.impuestos),
            'descuento': str(reservation.descuento),
            'total': str(reservation.total),
            'moneda': reservation.moneda,
        }

        invoice, created = (
            Factura.objects.get_or_create(
                reserva=reservation,
                defaults={
                    'cliente': reservation.cliente,
                    'numero_factura': Factura.generar_numero_factura(),
                    'fecha_emision': timezone.now(),
                    'descripcion': (
                        f'Reserva {reservation.codigo} por '
                        f'{reservation.numero_noches} noche(s).'
                    ),
                    'fecha_entrada': reservation.fecha_entrada,
                    'fecha_salida': reservation.fecha_salida,
                    'numero_noches': reservation.numero_noches,
                    'subtotal': reservation.subtotal,
                    'impuestos': reservation.impuestos,
                    'descuento': reservation.descuento,
                    'total': reservation.total,
                    'moneda': reservation.moneda,
                    'metodo_pago': payment.metodo_pago,
                    'estado': 'pagada',
                    'detalle_lineas': detalle_lineas,
                },
            )
        )

        if not created and not invoice.detalle_lineas:
            raise serializers.ValidationError({
                'factura': (
                    'La reserva ya tiene una factura sin el detalle inmutable '
                    'requerido. No se puede procesar el pago automáticamente.'
                ),
            })

        return payment, invoice