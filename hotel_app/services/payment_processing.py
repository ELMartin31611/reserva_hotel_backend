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
            payment_method
            == 'transferencia'
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
                'Pago académico registrado '
                'mediante StayBooking. '
                'No se almacenaron datos '
                'bancarios sensibles.'
            ),
        )

        reservation.estado = 'confirmada'
        reservation.save(
            update_fields=[
                'estado',
                'updated_at',
            ],
        )

        invoice, created = (
            Factura.objects.get_or_create(
                reserva=reservation,
                defaults={
                    'cliente': (
                        reservation.cliente
                    ),
                    'numero_factura': (
                        Factura
                        .generar_numero_factura()
                    ),
                    'fecha_emision': (
                        timezone.now()
                    ),
                    'descripcion': (
                        f'Reserva '
                        f'{reservation.codigo} '
                        f'por '
                        f'{reservation.numero_noches} '
                        'noche(s).'
                    ),
                    'fecha_entrada': (
                        reservation.fecha_entrada
                    ),
                    'fecha_salida': (
                        reservation.fecha_salida
                    ),
                    'numero_noches': (
                        reservation.numero_noches
                    ),
                    'subtotal': (
                        reservation.subtotal
                    ),
                    'impuestos': (
                        reservation.impuestos
                    ),
                    'descuento': (
                        reservation.descuento
                    ),
                    'total': (
                        reservation.total
                    ),
                    'moneda': (
                        reservation.moneda
                    ),
                    'metodo_pago': (
                        payment.metodo_pago
                    ),
                    'estado': 'pagada',
                },
            )
        )

        if not created:
            invoice.cliente = (
                reservation.cliente
            )
            invoice.fecha_emision = (
                timezone.now()
            )
            invoice.descripcion = (
                f'Reserva '
                f'{reservation.codigo} por '
                f'{reservation.numero_noches} '
                'noche(s).'
            )
            invoice.fecha_entrada = (
                reservation.fecha_entrada
            )
            invoice.fecha_salida = (
                reservation.fecha_salida
            )
            invoice.numero_noches = (
                reservation.numero_noches
            )
            invoice.subtotal = (
                reservation.subtotal
            )
            invoice.impuestos = (
                reservation.impuestos
            )
            invoice.descuento = (
                reservation.descuento
            )
            invoice.total = (
                reservation.total
            )
            invoice.moneda = (
                reservation.moneda
            )
            invoice.metodo_pago = (
                payment.metodo_pago
            )
            invoice.estado = 'pagada'
            invoice.save()

        return payment, invoice