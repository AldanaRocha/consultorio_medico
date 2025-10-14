from .models import Turno
from django.views.generic import ListView, CreateView ,UpdateView , DeleteView
from django.urls import reverse_lazy

class listaTurnos(ListView):
    model= Turno
    template_name = 'turnos.html'


class CrearTurno(CreateView):
    model= Turno
    template_name = 'crear_turno.html'
    fields = ['fecha', 'paciente', 'dni','obrasocial','especialidad']

    def get_success_url(self):
     return reverse_lazy('lista_turnos')
    
class EditarTurno(UpdateView):
   model = Turno
   template_name = 'editar_turno.html'
   fields = ['fecha', 'paciente', 'dni','obrasocial','especialidad']
   success_url = reverse_lazy ('lista_turnos')


class eliminarTurno(DeleteView):
   model = Turno
   success_url = reverse_lazy('lista_turnos')
   




# Create your views here.
