from .models import Especialidad
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages


# Mixin personalizado para verificar si es admin
class EsAdminMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff
    
    def handle_no_permission(self):
        messages.error(self.request, 'No tienes permisos para acceder a esta página.')
        return super().handle_no_permission()


# LISTAR - Todos pueden ver
class ListadeEspecialidad(ListView):
    model = Especialidad
    template_name = 'Especialidades.html'
    
    def get_queryset(self):
        # Solo mostrar especialidades activas
        return Especialidad.objects.filter(activo=True)


# CREAR - Solo admin
class CrearEspecialidad(LoginRequiredMixin, EsAdminMixin, CreateView):
    model = Especialidad
    template_name = 'Crear_especialidad.html'
    fields = ['tipo', 'doctor', 'activo']
    
    def get_success_url(self):
        return reverse_lazy('lista_especialidades')


# EDITAR - Solo admin
class EditarEspecialida(LoginRequiredMixin, EsAdminMixin, UpdateView):
    model = Especialidad
    template_name = 'Editar_especialidad.html'
    fields = ['tipo', 'doctor', 'activo']
    success_url = reverse_lazy('lista_especialidades')


# ELIMINAR - Solo admin
class EliminarEspecialidad(LoginRequiredMixin, EsAdminMixin, DeleteView):
    model = Especialidad
    success_url = reverse_lazy('lista_especialidades')