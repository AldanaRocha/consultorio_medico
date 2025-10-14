from .views import ListadeEspecialidad, CrearEspecialidad, EditarEspecialida, EliminarEspecialidad
from django.urls import path

urlpatterns = [

path('', ListadeEspecialidad.as_view(), name = 'lista_especialidades'),

path('nueva/', CrearEspecialidad.as_view(), name= 'nueva_especialidad'),

path('<int:pk>/editar/', EditarEspecialida.as_view(), name = 'editar_especialidad'),

path('<int:pk>/eliminar/', EliminarEspecialidad.as_view(), name = 'eliminar_especialidad'),

]