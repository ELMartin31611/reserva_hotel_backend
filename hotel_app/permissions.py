from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    Lectura para usuarios autenticados.
    Escritura solo para administradores.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated

        return request.user and request.user.is_staff


class IsReservaOwnerOrAdmin(BasePermission):
    """
    Admin puede ver todo.
    Usuario normal solo puede ver objetos relacionados con sus reservas.
    """

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True

        if hasattr(obj, 'cliente'):
            return obj.cliente.perfil.user == request.user

        if hasattr(obj, 'reserva'):
            return obj.reserva.cliente.perfil.user == request.user

        return False


def user_owns_reserva(user, reserva):
    """
    Valida si una reserva pertenece al usuario autenticado.
    """
    if user and user.is_staff:
        return True

    try:
        return reserva.cliente.perfil.user == user
    except Exception:
        return False