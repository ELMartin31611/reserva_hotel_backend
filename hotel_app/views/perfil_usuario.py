from rest_framework import generics
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny
)

from hotel_app.models import PerfilUsuario

from hotel_app.serializers import (
    RegistroSerializer,
    PerfilUsuarioSerializer
)


class RegistroView(generics.CreateAPIView):

    serializer_class = RegistroSerializer
    permission_classes = [AllowAny]


class PerfilView(generics.RetrieveAPIView):

    serializer_class = PerfilUsuarioSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.perfil