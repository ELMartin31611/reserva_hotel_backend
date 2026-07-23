from django.db import IntegrityError
from django.db.models import ProtectedError
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.parsers import (
    FormParser,
    JSONParser,
    MultiPartParser,
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from hotel_app.models import (
    Hotel,
    MediaHotel,
    ReservaHabitacion,
    Servicio,
    TarifaHabitacion,
    Temporada,
    TipoHabitacionServicio,
)
from hotel_app.permissions import IsAdminOrReadOnly
from hotel_app.serializers.hotel import HotelSerializer
from hotel_app.serializers.habitacion import HabitacionSerializer
from hotel_app.serializers.media_hotel import MediaHotelSerializer
from hotel_app.serializers.servicio import ServicioSerializer
from hotel_app.serializers.temporada import TemporadaSerializer


class HotelViewSet(ModelViewSet):
    serializer_class = HotelSerializer
    permission_classes = [IsAdminOrReadOnly]

    parser_classes = [
        MultiPartParser,
        FormParser,
        JSONParser,
    ]

    filterset_fields = [
        'estado',
        'categoria_estrellas',
        'permite_mascotas',
    ]

    search_fields = [
        'nombre',
        'ruc',
        'telefono',
        'email',
        'descripcion',
    ]

    ordering_fields = [
        'id',
        'nombre',
        'categoria_estrellas',
        'created_at',
        'updated_at',
    ]

    ordering = ['id']

    def get_queryset(self):
        return (
            Hotel.objects
            .exclude(estado__iexact='eliminado')
            .order_by('id')
        )

    def destroy(self, request, *args, **kwargs):
        hotel = self.get_object()

        has_reservation_history = (
            ReservaHabitacion.objects
            .filter(
                habitacion__hotel=hotel,
            )
            .exists()
        )

        if not has_reservation_history:
            try:
                hotel.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except (ProtectedError, IntegrityError):
                pass

        # Conserva reservas, pagos y facturas, pero retira el hotel del sistema.
        hotel.estado = 'eliminado'
        hotel.save(
            update_fields=[
                'estado',
                'updated_at',
            ],
        )

        hotel.habitaciones.update(
            estado='inactiva',
        )

        hotel.tipos_habitacion.update(
            estado='inactivo',
        )

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(
        detail=True,
        methods=['get'],
        url_path='detalle',
    )
    def detalle(self, request, pk=None):
        hotel = self.get_object()
        rooms = hotel.habitaciones.exclude(
            estado__iexact='eliminada',
        ).exclude(
            estado__iexact='eliminado',
        ).select_related(
            'tipo_habitacion',
        ).prefetch_related(
            'imagenes',
            'tipo_habitacion__servicios_habitacion__servicio',
        )
        room_type_ids = list(
            rooms.values_list('tipo_habitacion_id', flat=True).distinct(),
        )
        relations = TipoHabitacionServicio.objects.filter(
            tipo_habitacion_id__in=room_type_ids,
        ).select_related('servicio', 'tipo_habitacion')
        service_ids = relations.values_list('servicio_id', flat=True)
        season_ids = TarifaHabitacion.objects.filter(
            tipo_habitacion_id__in=room_type_ids,
            is_active=True,
        ).values_list('temporada_id', flat=True)

        base = HotelSerializer(
            hotel,
            context={'request': request},
        ).data
        services_payload = ServicioSerializer(
            Servicio.objects.filter(
                id__in=service_ids,
                is_active=True,
            ).distinct(),
            many=True,
            context={'request': request},
        ).data

        relations_by_service = {}
        for relation in relations:
            relations_by_service.setdefault(
                relation.servicio_id,
                [],
            ).append({
                'tipo_habitacion_id': relation.tipo_habitacion_id,
                'tipo_habitacion_nombre': relation.tipo_habitacion.nombre,
                'incluido': relation.incluido,
                'precio_personalizado': (
                    str(relation.precio_personalizado)
                    if relation.precio_personalizado is not None
                    else None
                ),
            })

        for service in services_payload:
            compatibility = relations_by_service.get(service['id'], [])
            service['tipos_habitacion_compatibles'] = compatibility
            service['incluido_en_alguna_habitacion'] = any(
                item['incluido']
                for item in compatibility
            )

        base.update({
            'galeria': {
                'imagenes': MediaHotelSerializer(
                    MediaHotel.objects.filter(
                        hotel=hotel,
                        tipo='imagen',
                    ),
                    many=True,
                    context={'request': request},
                ).data,
                'videos': MediaHotelSerializer(
                    MediaHotel.objects.filter(
                        hotel=hotel,
                        tipo='video',
                    ),
                    many=True,
                    context={'request': request},
                ).data,
            },
            'habitaciones': HabitacionSerializer(
                rooms,
                many=True,
                context={'request': request},
            ).data,
            'servicios': services_payload,
            'temporadas': TemporadaSerializer(
                Temporada.objects.filter(
                    id__in=season_ids,
                    is_active=True,
                ).distinct(),
                many=True,
                context={'request': request},
            ).data,
        })
        return Response(base)