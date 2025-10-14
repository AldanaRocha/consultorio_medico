from .models import Especialidad
from django.views.generic import ListView,   CreateView,    UpdateView ,    DeleteView
from django.urls import reverse_lazy


class ListadeEspecialidad(ListView):
    model= Especialidad
    template_name='Especialidades.html'

class CrearEspecialidad(CreateView):
    model = Especialidad
    template_name = 'Crear_especialidad.html'
    fields = ['tipo','doctor']

    def get_success_url(self):
     return reverse_lazy('lista_especialidades')
  
class EditarEspecialida(UpdateView):
   model = Especialidad
   template_name = 'Editar_especialidad.html'
   fields = ['tipo', 'doctor']
   success_url = reverse_lazy ('lista_especialidades')

class EliminarEspecialidad(DeleteView):
   model= Especialidad
   success_url = reverse_lazy('lista_especialidades')
