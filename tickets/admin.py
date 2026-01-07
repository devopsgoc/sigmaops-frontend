"""
Configuración del Admin de Django para el sistema de tickets
"""
from django.contrib import admin
from .models import (
    Rol, Usuario, Estado, Categoria, Proveedor, 
    DataCenter, Elemento, Ticket, Observacion
)


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre']
    search_fields = ['nombre']


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'correo', 'rol', 'creado_en']
    list_filter = ['rol']
    search_fields = ['nombre', 'correo']


@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'descripcion']


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'descripcion']


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'contacto', 'activo']
    list_filter = ['activo']


@admin.register(DataCenter)
class DataCenterAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'ubicacion', 'tipo']
    list_filter = ['tipo']


@admin.register(Elemento)
class ElementoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre', 'tipo']
    list_filter = ['tipo']
    search_fields = ['nombre']


class ObservacionInline(admin.TabularInline):
    model = Observacion
    extra = 0
    readonly_fields = ['fecha']


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'titulo', 'prioridad', 'estado', 'categoria', 'dc', 'fecha_inicio']
    list_filter = ['estado', 'prioridad', 'categoria', 'dc', 'proveedor']
    search_fields = ['codigo', 'titulo', 'descripcion']
    date_hierarchy = 'fecha_inicio'
    inlines = [ObservacionInline]


@admin.register(Observacion)
class ObservacionAdmin(admin.ModelAdmin):
    list_display = ['id', 'ticket', 'tipo', 'usuario', 'fecha']
    list_filter = ['tipo']
    search_fields = ['comentario']
