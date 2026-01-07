"""
Modelos Django para el sistema de tickets claro_sigmaops
Generados mediante ingeniería inversa del dump SQL
"""
from django.db import models


class Rol(models.Model):
    """Roles de usuario: Administrador, Super Admin, Operador, Visor"""
    nombre = models.CharField(max_length=50, unique=True)

    class Meta:
        managed = False
        db_table = 'roles'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.nombre


class Usuario(models.Model):
    """Usuarios del sistema con autenticación propia"""
    nombre = models.CharField(max_length=100)
    correo = models.CharField(max_length=150, unique=True)
    password_hash = models.CharField(max_length=255)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return self.nombre


class Estado(models.Model):
    """Estados de tickets: Pendiente, En Proceso, Cerrado, etc."""
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'estados'
        verbose_name = 'Estado'
        verbose_name_plural = 'Estados'

    def __str__(self):
        return self.nombre


class Categoria(models.Model):
    """Categorías: Incidente, Requerimiento, Proyecto, etc."""
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'categorias'
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.nombre


class Proveedor(models.Model):
    """Proveedores externos: HPE, NTT, RedHat, DELL"""
    nombre = models.CharField(max_length=100)
    contacto = models.CharField(max_length=150, blank=True, null=True)
    correo_contacto = models.CharField(max_length=150, blank=True, null=True)
    telefono_contacto = models.CharField(max_length=50, blank=True, null=True)
    pais = models.CharField(max_length=100, blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'proveedores'
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'

    def __str__(self):
        return self.nombre


class DataCenter(models.Model):
    """Data Centers: DCL, DCC, DCANTF, DCCHI"""
    TIPO_CHOICES = [
        ('Principal', 'Principal'),
        ('Backup', 'Backup'),
        ('Secundario', 'Secundario'),
    ]
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=150, blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='Principal')

    class Meta:
        managed = False
        db_table = 'data_centers'
        verbose_name = 'Data Center'
        verbose_name_plural = 'Data Centers'

    def __str__(self):
        return f"{self.nombre} ({self.ubicacion})"


class Elemento(models.Model):
    """Elementos de infraestructura: HOST, CLF, ENM, SWITCH, etc."""
    TIPO_CHOICES = [
        ('HOST', 'HOST'),
        ('CLF', 'CLF'),
        ('ENM', 'ENM'),
        ('SWITCH', 'SWITCH'),
        ('DCGW', 'DCGW'),
        ('EAS', 'EAS'),
        ('OPC', 'OPC'),
        ('OTRO', 'OTRO'),
    ]
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='OTRO')
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'elementos'
        verbose_name = 'Elemento'
        verbose_name_plural = 'Elementos'

    def __str__(self):
        return f"{self.nombre} ({self.tipo})"


class Ticket(models.Model):
    """Tabla principal de tickets de infraestructura"""
    PRIORIDAD_CHOICES = [
        ('Baja', 'Baja'),
        ('Media', 'Media'),
        ('Alta', 'Alta'),
        ('Crítica', 'Crítica'),
    ]
    
    codigo = models.CharField(max_length=50, unique=True)
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='Media')
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT, db_column='estado_id')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, db_column='categoria_id')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True, db_column='proveedor_id')
    elemento = models.ForeignKey(Elemento, on_delete=models.SET_NULL, null=True, blank=True, db_column='elemento_id')
    dc = models.ForeignKey(DataCenter, on_delete=models.SET_NULL, null=True, blank=True, db_column='dc_id')
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_actualizacion = models.DateField(blank=True, null=True)
    fecha_cierre = models.DateField(blank=True, null=True)
    usuario_creador = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, 
        related_name='tickets_creados', db_column='usuario_creador_id'
    )
    usuario_asignado = models.ForeignKey(
        Usuario, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='tickets_asignados', db_column='usuario_asignado_id'
    )
    # Campo calculado (GENERATED en MySQL)
    duracion_dias = models.IntegerField(blank=True, null=True, editable=False)

    class Meta:
        managed = False
        db_table = 'tickets'
        verbose_name = 'Ticket'
        verbose_name_plural = 'Tickets'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f"{self.codigo} - {self.titulo[:50]}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('ticket_detail', kwargs={'pk': self.pk})

    @property
    def prioridad_badge(self):
        """Retorna clase CSS para badge de prioridad"""
        badges = {
            'Baja': 'badge-low',
            'Media': 'badge-medium',
            'Alta': 'badge-high',
            'Crítica': 'badge-critical',
        }
        return badges.get(self.prioridad, 'badge-medium')


class Observacion(models.Model):
    """Comentarios y seguimiento de tickets"""
    TIPO_CHOICES = [
        ('General', 'General'),
        ('Técnica', 'Técnica'),
        ('Seguimiento', 'Seguimiento'),
        ('Escalamiento', 'Escalamiento'),
    ]
    
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='observaciones')
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    comentario = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='General')
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'observaciones'
        verbose_name = 'Observación'
        verbose_name_plural = 'Observaciones'
        ordering = ['-fecha']

    def __str__(self):
        return f"Obs. {self.ticket.codigo} - {self.tipo}"


class Asignacion(models.Model):
    """Asignaciones de tickets a usuarios"""
    ROL_CHOICES = [
        ('Responsable', 'Responsable'),
        ('Colaborador', 'Colaborador'),
        ('Supervisor', 'Supervisor'),
    ]
    
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='asignaciones')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    rol_asignacion = models.CharField(max_length=20, choices=ROL_CHOICES, default='Responsable')
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        managed = False
        db_table = 'asignaciones'
        verbose_name = 'Asignación'
        verbose_name_plural = 'Asignaciones'

    def __str__(self):
        return f"{self.usuario.nombre} - {self.ticket.codigo}"


class ArchivoAdjunto(models.Model):
    """Archivos adjuntos a tickets"""
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='archivos')
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    nombre_archivo = models.CharField(max_length=255)
    tipo_mime = models.CharField(max_length=100, blank=True, null=True)
    ruta_almacenamiento = models.CharField(max_length=500, blank=True, null=True)
    tamano_bytes = models.BigIntegerField(blank=True, null=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'archivos_adjuntos'
        verbose_name = 'Archivo Adjunto'
        verbose_name_plural = 'Archivos Adjuntos'

    def __str__(self):
        return self.nombre_archivo


class EstadoHistorico(models.Model):
    """Historial de cambios de estado de tickets"""
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='historial_estados')
    estado = models.ForeignKey(Estado, on_delete=models.PROTECT)
    fecha_cambio = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    comentario = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'estados_historicos'
        verbose_name = 'Estado Histórico'
        verbose_name_plural = 'Estados Históricos'
        ordering = ['-fecha_cambio']


class SlaControl(models.Model):
    """Control de SLA de tickets"""
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='sla')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_respuesta = models.DateTimeField(blank=True, null=True)
    fecha_cierre = models.DateTimeField(blank=True, null=True)
    tiempo_objetivo_horas = models.IntegerField(default=48)
    # Campos GENERATED en MySQL
    tiempo_real_horas = models.IntegerField(blank=True, null=True, editable=False)
    cumplimiento = models.BooleanField(blank=True, null=True, editable=False)

    class Meta:
        managed = False
        db_table = 'sla_control'
        verbose_name = 'Control SLA'
        verbose_name_plural = 'Controles SLA'


class RelacionTicket(models.Model):
    """Relaciones entre tickets"""
    TIPO_CHOICES = [
        ('Depende de', 'Depende de'),
        ('Relacionado con', 'Relacionado con'),
        ('Duplicado de', 'Duplicado de'),
        ('Sigue a', 'Sigue a'),
    ]
    
    ticket_padre = models.ForeignKey(
        Ticket, on_delete=models.CASCADE, 
        related_name='tickets_hijos', db_column='ticket_padre_id'
    )
    ticket_hijo = models.ForeignKey(
        Ticket, on_delete=models.CASCADE,
        related_name='tickets_padres', db_column='ticket_hijo_id'
    )
    tipo_relacion = models.CharField(max_length=20, choices=TIPO_CHOICES, default='Relacionado con')

    class Meta:
        managed = False
        db_table = 'relacion_tickets'
        verbose_name = 'Relación de Ticket'
        verbose_name_plural = 'Relaciones de Tickets'


class Auditoria(models.Model):
    """Registro de auditoría del sistema"""
    ACCION_CHOICES = [
        ('INSERT', 'INSERT'),
        ('UPDATE', 'UPDATE'),
        ('DELETE', 'DELETE'),
        ('LOGIN', 'LOGIN'),
        ('LOGOUT', 'LOGOUT'),
    ]
    
    entidad = models.CharField(max_length=50)
    accion = models.CharField(max_length=10, choices=ACCION_CHOICES)
    entidad_id = models.BigIntegerField(blank=True, null=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'auditoria'
        verbose_name = 'Auditoría'
        verbose_name_plural = 'Auditorías'
        ordering = ['-fecha']
