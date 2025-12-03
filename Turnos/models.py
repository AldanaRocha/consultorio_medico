from django.db import models
from django.contrib.auth.models import User
from Especialidad.models import Especialidad
from django.urls import reverse


class Turno(models.Model):
    ESTADO_PAGO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('cancelado', 'Cancelado'),
    ]
    
    TIPO_PAGO_CHOICES = [
        ('completo', 'Pago Completo'),
        ('senia', 'Seña'),
    ]
    
    # Información del turno
    fecha = models.DateField(verbose_name="Fecha del turno")
    dni = models.IntegerField(verbose_name="DNI")
    obrasocial = models.CharField(max_length=100, null=True, blank=True, verbose_name="Obra Social")
    paciente = models.CharField(max_length=200, verbose_name="Paciente")
    email = models.EmailField(null=True, blank=True, verbose_name="Email")
    especialidad = models.ForeignKey(Especialidad, on_delete=models.CASCADE, related_name='turnos')
    
    # Usuario del sistema (opcional - para vincular con cuenta)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='turnos')
    
    # Información de pago
    pago_total = models.BooleanField(default=False, verbose_name="Pago Total")
    pago_senia = models.BooleanField(default=False, verbose_name="Pago Seña")
    tipo_pago = models.CharField(max_length=20, choices=TIPO_PAGO_CHOICES, blank=True, null=True, verbose_name="Tipo de Pago")  # ← AGREGAR ESTA LÍNEA
    monto_pagado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Monto Pagado")
    estado_pago = models.CharField(max_length=20, choices=ESTADO_PAGO_CHOICES, default='pendiente', verbose_name="Estado del Pago")
    
    # Mercado Pago
    preference_id = models.CharField(max_length=100, blank=True, null=True)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True, verbose_name="Activo")
    
    class Meta:
        verbose_name = 'Turno'
        verbose_name_plural = 'Turnos'
        ordering = ['-fecha', '-fecha_creacion']  # Más recientes primero
        permissions = [
            ("puede_ver_todos_turnos", "Puede ver todos los turnos"),
            ("puede_gestionar_turnos", "Puede gestionar turnos"),
        ]
    
    def __str__(self):
        return f"{self.paciente} - {self.fecha} - {self.especialidad.tipo}"
    
    def get_absolute_url(self):
        return reverse('detalle_turno', kwargs={'pk': self.pk})