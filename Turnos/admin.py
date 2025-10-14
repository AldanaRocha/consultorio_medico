from django.contrib import admin
from .models import Turno


admin.site.register(Turno)
class Turnoadmin(admin.ModelAdmin):
    lista= ['fecha', 'dni','obrasocial','paciente','especialidad']
    