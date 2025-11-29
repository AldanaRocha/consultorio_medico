from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib import messages
from django.views import View


class RegistroView(View):
    """Vista para registrar nuevos pacientes"""
    
    def get(self, request):
        # Si ya está logueado, redirigir
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, 'usuarios/registro.html')
    
    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # Validaciones
        if not username or not email or not password:
            messages.error(request, 'Todos los campos son obligatorios.')
            return redirect('registro')
        
        if password != password_confirm:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('registro')
        
        if len(password) < 6:
            messages.error(request, 'La contraseña debe tener al menos 6 caracteres.')
            return redirect('registro')
        
        # Verificar si el usuario ya existe
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya está en uso.')
            return redirect('registro')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'El email ya está registrado.')
            return redirect('registro')
        
        # Crear usuario paciente
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=False,
            is_superuser=False
        )
        
        # Login automático después del registro
        login(request, user)
        messages.success(request, f'¡Bienvenido {username}! Tu cuenta ha sido creada exitosamente.')
        return redirect('/')


class LoginView(View):
    """Vista para iniciar sesión"""
    
    def get(self, request):
        # Si ya está logueado, redirigir
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, 'usuarios/login.html')
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Por favor completa todos los campos.')
            return redirect('login')
        
        # Autenticar usuario
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.username}!')
            
            # Redirigir a la página que intentaba acceder o a home
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
            return redirect('login')


class LogoutView(View):
    """Vista para cerrar sesión"""
    
    def get(self, request):
        logout(request)
        messages.success(request, 'Has cerrado sesión correctamente.')
        return redirect('login')