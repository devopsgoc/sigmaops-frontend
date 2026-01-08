"""
Vistas del sistema de tickets
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.db.models import Count, Q
from django.contrib import messages
from .models import Ticket, Observacion, Estado, Categoria, Proveedor, DataCenter, Elemento, Usuario
from .forms import TicketForm, ObservacionForm
from .permissions import PuedeCrearMixin, PuedeEditarMixin


@login_required
def dashboard(request):
    """Dashboard principal con estadísticas y filtros"""
    # Contadores generales
    total_tickets = Ticket.objects.count()
    tickets_pendientes = Ticket.objects.filter(estado__nombre='Pendiente').count()
    tickets_en_proceso = Ticket.objects.filter(estado__nombre='En Proceso').count()
    tickets_cerrados = Ticket.objects.filter(estado__nombre='Cerrado').count()
    
    # Tickets por prioridad
    tickets_criticos = Ticket.objects.filter(prioridad='Crítica').count()
    tickets_alta = Ticket.objects.filter(prioridad='Alta').count()
    
    # Tickets por categoría
    tickets_por_categoria = Categoria.objects.annotate(
        total=Count('ticket')
    ).filter(total__gt=0).values('nombre', 'total')
    
    # Tickets por data center
    tickets_por_dc = DataCenter.objects.annotate(
        total=Count('ticket')
    ).filter(total__gt=0).values('nombre', 'total')
    
    # Filtrar tickets según el parámetro GET
    filtro = request.GET.get('filtro', 'todos')
    valor = request.GET.get('valor', '')
    tickets_filtrados = Ticket.objects.select_related(
        'estado', 'categoria', 'proveedor', 'dc'
    )
    
    if filtro == 'pendiente':
        tickets_filtrados = tickets_filtrados.filter(estado__nombre='Pendiente')
    elif filtro == 'proceso':
        tickets_filtrados = tickets_filtrados.filter(estado__nombre='En Proceso')
    elif filtro == 'cerrado':
        tickets_filtrados = tickets_filtrados.filter(estado__nombre='Cerrado')
    elif filtro == 'critico':
        tickets_filtrados = tickets_filtrados.filter(prioridad='Crítica')
    elif filtro == 'alta':
        tickets_filtrados = tickets_filtrados.filter(prioridad='Alta')
    elif filtro == 'categoria' and valor:
        tickets_filtrados = tickets_filtrados.filter(categoria__nombre=valor)
    elif filtro == 'dc' and valor:
        tickets_filtrados = tickets_filtrados.filter(dc__nombre=valor)
    
    tickets_filtrados = tickets_filtrados.order_by('-fecha_inicio')
    
    context = {
        'total_tickets': total_tickets,
        'tickets_pendientes': tickets_pendientes,
        'tickets_en_proceso': tickets_en_proceso,
        'tickets_cerrados': tickets_cerrados,
        'tickets_criticos': tickets_criticos,
        'tickets_alta': tickets_alta,
        'tickets_por_categoria': tickets_por_categoria,
        'tickets_por_dc': tickets_por_dc,
        'tickets_filtrados': tickets_filtrados,
    }
    return render(request, 'tickets/dashboard.html', context)


class TicketListView(LoginRequiredMixin, ListView):
    """Listado de tickets con filtros"""
    model = Ticket
    template_name = 'tickets/ticket_list.html'
    context_object_name = 'tickets'
    paginate_by = 15
    
    def get_queryset(self):
        queryset = Ticket.objects.select_related(
            'estado', 'categoria', 'proveedor', 'dc', 'usuario_asignado'
        )
        
        # Filtros
        estado = self.request.GET.get('estado')
        categoria = self.request.GET.get('categoria')
        prioridad = self.request.GET.get('prioridad')
        dc = self.request.GET.get('dc')
        busqueda = self.request.GET.get('q')
        
        if estado:
            queryset = queryset.filter(estado_id=estado)
        if categoria:
            queryset = queryset.filter(categoria_id=categoria)
        if prioridad:
            queryset = queryset.filter(prioridad=prioridad)
        if dc:
            queryset = queryset.filter(dc_id=dc)
        if busqueda:
            queryset = queryset.filter(
                Q(codigo__icontains=busqueda) | 
                Q(titulo__icontains=busqueda) |
                Q(descripcion__icontains=busqueda)
            )
        
        return queryset.order_by('-fecha_inicio')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estados'] = Estado.objects.all()
        context['categorias'] = Categoria.objects.all()
        context['data_centers'] = DataCenter.objects.all()
        context['prioridades'] = ['Baja', 'Media', 'Alta', 'Crítica']
        return context


class TicketDetailView(LoginRequiredMixin, DetailView):
    """Detalle de un ticket con observaciones"""
    model = Ticket
    template_name = 'tickets/ticket_detail.html'
    context_object_name = 'ticket'
    
    def get_queryset(self):
        return Ticket.objects.select_related(
            'estado', 'categoria', 'proveedor', 'dc', 
            'elemento', 'usuario_creador', 'usuario_asignado'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['observaciones'] = self.object.observaciones.select_related('usuario').order_by('-fecha')
        context['form_observacion'] = ObservacionForm()
        return context


class TicketCreateView(PuedeCrearMixin, LoginRequiredMixin, CreateView):
    """Crear nuevo ticket - Requiere rol: Super Admin, Administrador, Operador"""
    model = Ticket
    form_class = TicketForm
    template_name = 'tickets/ticket_form.html'
    
    def get_success_url(self):
        messages.success(self.request, f'Ticket {self.object.codigo} creado exitosamente.')
        return self.object.get_absolute_url()


class TicketUpdateView(PuedeEditarMixin, LoginRequiredMixin, UpdateView):
    """Editar ticket existente - Requiere rol: Super Admin, Administrador, Operador"""
    model = Ticket
    form_class = TicketForm
    template_name = 'tickets/ticket_form.html'
    
    def get_success_url(self):
        messages.success(self.request, f'Ticket {self.object.codigo} actualizado.')
        return self.object.get_absolute_url()


def agregar_observacion(request, pk):
    """Agregar observación a un ticket"""
    ticket = get_object_or_404(Ticket, pk=pk)
    
    if request.method == 'POST':
        form = ObservacionForm(request.POST)
        if form.is_valid():
            observacion = form.save(commit=False)
            observacion.ticket = ticket
            # Aquí se podría asignar el usuario logueado
            observacion.save()
            messages.success(request, 'Observación agregada correctamente.')
    
    return redirect('ticket_detail', pk=pk)
