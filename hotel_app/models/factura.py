import uuid

from django.db import models
from django.utils import timezone


class Factura(models.Model):
    ESTADO_CHOICES = [
        ('emitida', 'Emitida'),
        ('pagada', 'Pagada'),
        ('anulada', 'Anulada'),
    ]

    reserva = models.OneToOneField(
        'hotel_app.Reserva',
        on_delete=models.CASCADE,
        related_name='factura',
    )

    cliente = models.ForeignKey(
        'hotel_app.Cliente',
        on_delete=models.PROTECT,
        related_name='facturas',
    )

    numero_factura = models.CharField(
        max_length=40,
        unique=True,
    )

    fecha_emision = models.DateTimeField(
        default=timezone.now,
    )

    descripcion = models.TextField(
        blank=True,
        null=True,
    )

    fecha_entrada = models.DateField()

    fecha_salida = models.DateField()

    numero_noches = models.PositiveIntegerField()

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    impuestos = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    descuento = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    moneda = models.CharField(
        max_length=10,
        default='USD',
    )

    metodo_pago = models.CharField(
        max_length=30,
        blank=True,
        null=True,
    )

    estado = models.CharField(
        max_length=30,
        choices=ESTADO_CHOICES,
        default='emitida',
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'
        ordering = ['-fecha_emision']

    @staticmethod
    def generar_numero_factura():
        fecha = timezone.localdate().strftime('%Y%m%d')
        identificador = uuid.uuid4().hex[:10].upper()

        return f'F001-{fecha}-{identificador}'

    @classmethod
    def generar_desde_reserva(
        cls,
        reserva,
        metodo_pago=None,
    ):
        factura, _ = cls.objects.get_or_create(
            reserva=reserva,
            defaults={
                'cliente': reserva.cliente,
                'numero_factura': (
                    cls.generar_numero_factura()
                ),
                'fecha_emision': timezone.now(),
                'descripcion': (
                    f'Reserva {reserva.codigo} por '
                    f'{reserva.numero_noches} noche(s).'
                ),
                'fecha_entrada': reserva.fecha_entrada,
                'fecha_salida': reserva.fecha_salida,
                'numero_noches': reserva.numero_noches,
                'subtotal': reserva.subtotal,
                'impuestos': reserva.impuestos,
                'descuento': reserva.descuento,
                'total': reserva.total,
                'moneda': reserva.moneda,
                'metodo_pago': metodo_pago,
                'estado': 'pagada',
            },
        )

        return factura

    def __str__(self):
        return self.numero_factura