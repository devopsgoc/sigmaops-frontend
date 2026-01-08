"""
Middleware para obtener el rol del usuario desde la tabla usuarios de MariaDB
"""
from .models import Usuario


class RolMiddleware:
    """
    Middleware que agrega el rol del usuario al request.
    Busca el usuario en la tabla 'usuarios' por el email y asigna su rol.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Inicializar atributos
        request.usuario_db = None
        request.rol_nombre = None
        request.es_super_admin = False
        request.es_administrador = False
        request.es_operador = False
        request.es_visor = False
        
        if request.user.is_authenticated:
            # Buscar usuario en la tabla usuarios por email
            try:
                usuario = Usuario.objects.select_related('rol').filter(
                    correo=request.user.email
                ).first()
                
                if not usuario:
                    # Intentar buscar por username si no tiene email
                    usuario = Usuario.objects.select_related('rol').filter(
                        correo=request.user.username
                    ).first()
                
                if usuario:
                    request.usuario_db = usuario
                    request.rol_nombre = usuario.rol.nombre
                    
                    # Flags de permisos
                    request.es_super_admin = usuario.rol.nombre == 'Super Admin'
                    request.es_administrador = usuario.rol.nombre == 'Administrador' or request.es_super_admin
                    request.es_operador = usuario.rol.nombre == 'Operador' or request.es_administrador
                    request.es_visor = usuario.rol.nombre == 'Visor' or request.es_operador
                    
            except Exception as e:
                # Si hay error, el usuario no tiene rol asignado
                print(f"Error buscando rol: {e}")
        
        response = self.get_response(request)
        return response
