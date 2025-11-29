from django.db import models

class Especialidad(models.Model):
    tipo = models.CharField(max_length=100, verbose_name="Tipo de Especialidad")
    doctor = models.CharField(max_length=150, verbose_name="Doctor")
    activo = models.BooleanField(default=True, verbose_name="Activo")  # Para desactivar sin eliminar

    
    class Meta:
        verbose_name = "Especialidad"
        verbose_name_plural = "Especialidades"
        ordering = ['tipo']  # Ordenar alfabéticamente
        permissions = [
            ("puede_gestionar_especialidades", "Puede gestionar especialidades"),
        ]
    
    def __str__(self):
        return f'{self.tipo} - Dr/a. {self.doctor}'