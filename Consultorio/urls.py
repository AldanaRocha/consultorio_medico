from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from usuarios.views import RegistroView, LoginView, LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Página principal
    path('', TemplateView.as_view(template_name='base.html'), name='home'),  
    path('aboutus/', TemplateView.as_view(template_name='aboutus.html'), name='aboutus'),
    
    # Autenticación (rutas individuales)
    path('registro/', RegistroView.as_view(), name='registro'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Apps
    path('esp/', include('Especialidad.urls')),
    path('turno/', include('Turnos.urls')),
]