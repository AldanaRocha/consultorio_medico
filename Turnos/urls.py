from .views import listaTurnos , CrearTurno, EditarTurno, eliminarTurno
from django.urls import path


urlpatterns=[

 path('', listaTurnos.as_view(), name='lista_turnos'),
 
 path('nuevo/', CrearTurno.as_view(), name= 'crear_turno'),

 path('<int:pk>/editar/', EditarTurno.as_view(), name='editar_turno'),

 path('<int:pk>/eliminar/', eliminarTurno.as_view(), name='eliminar_turno'),

]
