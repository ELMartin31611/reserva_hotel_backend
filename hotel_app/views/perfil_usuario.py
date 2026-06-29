from rest_framework import generics, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny

from hotel_app.models import PerfilUsuario
from hotel_app.serializers import RegistroSerializer, PerfilUsuarioSerializer
from hotel_app.permissions import IsAdminOrReadOnly


class RegistroView(generics.CreateAPIView):
    serializer_class = RegistroSerializer
    permission_classes = [AllowAny]


class PerfilView(generics.RetrieveAPIView):
    serializer_class = PerfilUsuarioSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.perfil


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
