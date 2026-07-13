from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from hotel_app.models import PerfilUsuario
from hotel_app.permissions import IsAdminOrReadOnly
from hotel_app.serializers import (
    PerfilUsuarioSerializer,
    RegistroSerializer,
)


class RegistroView(generics.CreateAPIView):
    serializer_class = RegistroSerializer
    permission_classes = [AllowAny]


class PerfilView(generics.RetrieveAPIView):
    serializer_class = PerfilUsuarioSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user

        rol_inicial = (
            'ADMIN'
            if user.is_staff or user.is_superuser
            else 'USUARIO'
        )

        perfil, _ = PerfilUsuario.objects.get_or_create(
            user=user,
            defaults={
                'rol': rol_inicial,
                'estado': 'ACTIVO',
            },
        )

        if (user.is_staff or user.is_superuser) and perfil.rol != 'ADMIN':
            perfil.rol = 'ADMIN'
            perfil.estado = 'ACTIVO'
            perfil.save(
                update_fields=[
                    'rol',
                    'estado',
                    'updated_at',
                ],
            )

        return perfil


class PerfilUsuarioViewSet(viewsets.ModelViewSet):
    queryset = PerfilUsuario.objects.select_related('user').all()
    serializer_class = PerfilUsuarioSerializer
    permission_classes = [IsAdminOrReadOnly]

    filterset_fields = [
        'rol',
        'estado',
    ]

    search_fields = [
        'user__username',
        'user__email',
        'telefono',
    ]

    ordering_fields = [
        'id',
        'rol',
        'estado',
        'created_at',
    ]

    ordering = ['id']