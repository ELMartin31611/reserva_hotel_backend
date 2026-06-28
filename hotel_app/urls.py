from django.urls import path

from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

from hotel_app.views import (
    RegistroView,
    PerfilView,

    ClienteViewSet,
    DireccionClienteViewSet,
    DocumentoClienteViewSet,

    CargoEmpleadoViewSet,
    TurnoViewSet,
    EmpleadoViewSet,
    EmpleadoTurnoViewSet
)

router = DefaultRouter()

# CLIENTES

router.register(
    'clientes',
    ClienteViewSet
)

router.register(
    'direcciones',
    DireccionClienteViewSet
)

router.register(
    'documentos',
    DocumentoClienteViewSet
)

# EMPLEADOS

router.register(
    'cargos',
    CargoEmpleadoViewSet
)

router.register(
    'turnos',
    TurnoViewSet
)

router.register(
    'empleados',
    EmpleadoViewSet
)

router.register(
    'empleado-turnos',
    EmpleadoTurnoViewSet
)

urlpatterns = [

    path(
        'register/',
        RegistroView.as_view(),
        name='register'
    ),

    path(
        'login/',
        TokenObtainPairView.as_view(),
        name='login'
    ),

    path(
        'token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),

    path(
        'perfil/',
        PerfilView.as_view(),
        name='perfil'
    ),

]

urlpatterns += router.urls