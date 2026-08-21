from rest_framework.permissions import BasePermission
from .models import Perfil

class EsAdmin(BasePermission):
    """Permite acceso solo a usuarios sin tienda asociada (administradores)."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        perfil = Perfil.objects.filter(usuario=request.user).first()
        return perfil is None or perfil.tienda is None