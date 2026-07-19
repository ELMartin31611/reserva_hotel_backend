from rest_framework.permissions import BasePermission, SAFE_METHODS


def user_is_admin(user):
    """
    Determina si el usuario autenticado tiene permisos administrativos.

    Se consideran administradores:
    - Superusuarios de Django.
    - Usuarios staff.
    - Usuarios con perfil ADMIN y estado ACTIVO.
    """
    if not user or not user.is_authenticated:
        return False

    if user.is_staff or user.is_superuser:
        return True

    try:
        return (
            user.perfil.rol == 'ADMIN'
            and user.perfil.estado == 'ACTIVO'
        )
    except Exception:
        return False


class IsAdminOrReadOnly(BasePermission):
    """
    Permite lectura pública con GET, HEAD y OPTIONS.

    Las operaciones POST, PUT, PATCH y DELETE solamente están
    disponibles para administradores.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return user_is_admin(request.user)


class IsReservaOwnerOrAdmin(BasePermission):
    """
    Permite que los administradores accedan a cualquier objeto.

    Los clientes solamente pueden acceder a objetos relacionados
    con sus propias reservas.
    """

    def has_object_permission(self, request, view, obj):
        if user_is_admin(request.user):
            return True

        if hasattr(obj, 'cliente'):
            return obj.cliente.perfil.user == request.user

        if hasattr(obj, 'reserva'):
            return obj.reserva.cliente.perfil.user == request.user

        return False


def user_owns_reserva(user, reserva):
    """
    Comprueba si una reserva pertenece al usuario autenticado.

    Los administradores pueden acceder a todas las reservas.
    """
    if user_is_admin(user):
        return True

    try:
        return reserva.cliente.perfil.user == user
    except Exception:
        return False