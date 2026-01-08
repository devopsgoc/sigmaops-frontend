"""
Decoradores y mixins para control de acceso basado en roles
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin


def rol_requerido(*roles_permitidos):
    """
    Decorador para vistas basadas en función.
    Verifica que el usuario tenga uno de los roles permitidos.
    
    Uso:
    @rol_requerido('Super Admin', 'Administrador')
    def mi_vista(request):
        ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Super Admin siempre tiene acceso
            if request.es_super_admin:
                return view_func(request, *args, **kwargs)
            
            # Verificar si tiene alguno de los roles permitidos
            if request.rol_nombre in roles_permitidos:
                return view_func(request, *args, **kwargs)
            
            # No tiene permisos
            messages.error(request, 'No tienes permisos para acceder a esta sección.')
            return redirect('dashboard')
        
        return wrapper
    return decorator


def puede_crear_tickets(view_func):
    """Permite: Super Admin, Administrador, Operador"""
    return rol_requerido('Super Admin', 'Administrador', 'Operador')(view_func)


def puede_editar_tickets(view_func):
    """Permite: Super Admin, Administrador, Operador"""
    return rol_requerido('Super Admin', 'Administrador', 'Operador')(view_func)


def puede_eliminar_tickets(view_func):
    """Permite: Super Admin, Administrador"""
    return rol_requerido('Super Admin', 'Administrador')(view_func)


def solo_administradores(view_func):
    """Permite: Super Admin, Administrador"""
    return rol_requerido('Super Admin', 'Administrador')(view_func)


class RolRequeridoMixin(AccessMixin):
    """
    Mixin para vistas basadas en clase.
    Define roles_permitidos en la clase que hereda.
    
    Uso:
    class MiVista(RolRequeridoMixin, View):
        roles_permitidos = ['Super Admin', 'Administrador']
    """
    roles_permitidos = []
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Super Admin siempre tiene acceso
        if getattr(request, 'es_super_admin', False):
            return super().dispatch(request, *args, **kwargs)
        
        # Verificar rol
        rol_nombre = getattr(request, 'rol_nombre', None)
        if rol_nombre and rol_nombre in self.roles_permitidos:
            return super().dispatch(request, *args, **kwargs)
        
        messages.error(request, 'No tienes permisos para acceder a esta sección.')
        return redirect('dashboard')


class PuedeCrearMixin(RolRequeridoMixin):
    """Super Admin, Administrador, Operador pueden crear"""
    roles_permitidos = ['Super Admin', 'Administrador', 'Operador']


class PuedeEditarMixin(RolRequeridoMixin):
    """Super Admin, Administrador, Operador pueden editar"""
    roles_permitidos = ['Super Admin', 'Administrador', 'Operador']


class PuedeEliminarMixin(RolRequeridoMixin):
    """Solo Super Admin y Administrador pueden eliminar"""
    roles_permitidos = ['Super Admin', 'Administrador']


class SoloAdminMixin(RolRequeridoMixin):
    """Solo Super Admin y Administrador"""
    roles_permitidos = ['Super Admin', 'Administrador']
