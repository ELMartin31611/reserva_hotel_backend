from datetime import date
from decimal import Decimal
from types import SimpleNamespace

from django.test import SimpleTestCase
from rest_framework import serializers

from hotel_app.services.pricing_calculator import PricingCalculator


class RoomPricingCalculatorTests(SimpleTestCase):
    def setUp(self):
        self.room = SimpleNamespace(
            numero='101',
            tipo_habitacion=SimpleNamespace(
                id=1,
                nombre='Familiar',
                capacidad_total=4,
                capacidad_extra=1,
                capacidad_maxima=5,
                capacidad_ninos=4,
            ),
        )
        self.rate = SimpleNamespace(
            id=1,
            tipo_habitacion_id=1,
            is_active=True,
            moneda='USD',
            precio_noche=Decimal('100.00'),
            precio_fin_semana=None,
            temporada=SimpleNamespace(
                nombre='General',
                is_active=True,
                fecha_inicio=date(2026, 1, 1),
                fecha_fin=date(2027, 1, 1),
            ),
        )

    def calculate(self, adults, children=0):
        return PricingCalculator.calculate_room_pricing(
            room=self.room,
            adults=adults,
            children=children,
            check_in=date(2026, 8, 3),
            nights=2,
            rates=[self.rate],
        )

    def test_included_guests_do_not_change_room_price(self):
        for adults in (1, 2, 4):
            with self.subTest(adults=adults):
                pricing = self.calculate(adults)
                self.assertEqual(
                    pricing['room_total_subtotal'],
                    Decimal('200.00'),
                )
                self.assertEqual(
                    pricing['extra_guests_subtotal'],
                    Decimal('0.00'),
                )

    def test_one_extra_guest_adds_fifty_percent_per_night(self):
        pricing = self.calculate(adults=5)

        self.assertEqual(
            pricing['extra_guests_subtotal'],
            Decimal('100.00'),
        )
        self.assertEqual(
            pricing['room_total_subtotal'],
            Decimal('300.00'),
        )

    def test_guests_above_maximum_capacity_are_rejected(self):
        with self.assertRaises(serializers.ValidationError):
            self.calculate(adults=6)
