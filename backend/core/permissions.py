from rest_framework import permissions
from .models import UsuarioHasRol

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permite acceso de lectura (GET) a cualquier usuario autenticado,
    pero solo permite escritura (POST, PUT, DELETE) si el usuario tiene el rol 'Administrador'.
    """
    def has_permission(self, request, view):
        # 1. Si no está autenticado, fuera.
        if not request.user or not request.user.is_authenticated:
            return False

        # 2. Si solo quiere ver (GET), cualquier usuario logueado puede pasar.
        if request.method in permissions.SAFE_METHODS:
            return True

        # 3. Si es Superusuario de Django, tiene permiso total.
        if request.user.is_superuser:
            return True

        # 4. Verificar si tiene un rol con privilegios de escritura
        admin_roles = ['Administrador', 'SUPERADMINISTRADOR', 'ADMINISTRADOR']
        return UsuarioHasRol.objects.filter(
            usuario_idusuarios=request.user,
            rol_idrol__nombre__in=admin_roles
        ).exists()
