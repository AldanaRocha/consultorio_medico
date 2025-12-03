from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.views import View
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Turno
from .utils import crear_preferencia_pago, verificar_pago
import json


# Mixin personalizado para verificar si es admin
class EsAdminMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff
    
    def handle_no_permission(self):
        messages.error(self.request, 'No tienes permisos para acceder a esta página.')
        return super().handle_no_permission()


class listaTurnos(LoginRequiredMixin, ListView):
    model = Turno
    template_name = 'turnos.html'
    
    def get_queryset(self):
        # Si es admin, muestra todos los turnos
        if self.request.user.is_superuser or self.request.user.is_staff:
            return Turno.objects.filter(activo=True)
        
        # Si es paciente, solo muestra sus turnos
        # Buscar por usuario o por DNI/email
        return Turno.objects.filter(
            activo=True
        ).filter(
            usuario=self.request.user
        ) | Turno.objects.filter(
            activo=True,
            email=self.request.user.email
        )


class CrearTurno(LoginRequiredMixin, CreateView):
    model = Turno
    template_name = 'crear_turno.html'
    fields = ['fecha', 'paciente', 'dni', 'email', 'obrasocial', 'especialidad']

    def form_valid(self, form):
        # Asociar el turno con el usuario logueado
        form.instance.usuario = self.request.user
        
        # Si el email está vacío, usar el email del usuario
        if not form.instance.email and self.request.user.email:
            form.instance.email = self.request.user.email
        
        # Guardar el objeto primero
        self.object = form.save()
        
        # Redirigir a seleccionar pago
        return redirect('seleccionar_pago', turno_id=self.object.id)


class SeleccionarPagoView(LoginRequiredMixin, View):
    """Vista para que el usuario elija entre pago completo o seña"""
    
    def get(self, request, turno_id):
        turno = get_object_or_404(Turno, id=turno_id)
        
        # Verificar que el turno pertenezca al usuario (excepto admin)
        if not (request.user.is_superuser or request.user.is_staff):
            if turno.usuario != request.user and turno.email != request.user.email:
                messages.error(request, 'No tienes permiso para ver este turno.')
                return redirect('lista_turnos')
        
        from django.conf import settings
        context = {
            'turno': turno,
            'monto_completo': getattr(settings, 'MONTO_TURNO_COMPLETO', 5000),
            'monto_senia': getattr(settings, 'MONTO_SENIA', 1500)
        }
        return render(request, 'seleccionar_pago.html', context)
    
    def post(self, request, turno_id):
        turno = get_object_or_404(Turno, id=turno_id)
        
        # Verificar que el turno pertenezca al usuario (excepto admin)
        if not (request.user.is_superuser or request.user.is_staff):
            if turno.usuario != request.user and turno.email != request.user.email:
                messages.error(request, 'No tienes permiso para modificar este turno.')
                return redirect('lista_turnos')
        
        tipo_pago = request.POST.get('tipo_pago')
        
        if tipo_pago not in ['completo', 'senia']:
            messages.error(request, 'Tipo de pago inválido')
            return redirect('seleccionar_pago', turno_id=turno_id)
        
        try:
            # Debug: verificar que el turno tenga id
            print(f"Turno ID: {turno.id}")
            print(f"Turno: {turno}")
            print(f"Especialidad: {turno.especialidad}")
            print(f"Especialidad tipo: {turno.especialidad.tipo}")
            
            # Crear preferencia en Mercado Pago
            preferencia = crear_preferencia_pago(turno, tipo_pago, request)
            
            # Guardar datos en el turno
            turno.preference_id = preferencia['preference_id']
            turno.tipo_pago = tipo_pago
            
            from django.conf import settings
            monto_completo = getattr(settings, 'MONTO_TURNO_COMPLETO', 5000)
            monto_senia = getattr(settings, 'MONTO_SENIA', 1500)
            
            turno.monto_pagado = monto_completo if tipo_pago == 'completo' else monto_senia
            turno.save()
            
            # Redirigir a Mercado Pago
            return redirect(preferencia['init_point'])
            
        except Exception as e:
            import traceback
            print(f"Error completo: {traceback.format_exc()}")
            messages.error(request, f'Error al procesar el pago: {str(e)}')
            return redirect('seleccionar_pago', turno_id=turno_id)

class PagoExitosoView(LoginRequiredMixin, View):
    """Vista cuando el pago fue exitoso"""
    
    def get(self, request, turno_id):
        turno = get_object_or_404(Turno, id=turno_id)
        
        # Verificar que el turno pertenezca al usuario (excepto admin)
        if not (request.user.is_superuser or request.user.is_staff):
            if turno.usuario != request.user and turno.email != request.user.email:
                messages.error(request, 'No tienes permiso para ver este turno.')
                return redirect('lista_turnos')
        
        payment_id = request.GET.get('payment_id')
        
        if payment_id:
            turno.payment_id = payment_id
            turno.estado_pago = 'aprobado'
            
            # Actualizar flags según tipo de pago
            if turno.tipo_pago == 'completo':
                turno.pago_total = True
                turno.pago_senia = False
            elif turno.tipo_pago == 'senia':
                turno.pago_senia = True
                turno.pago_total = False
            else:
                # Si por alguna razón tipo_pago está vacío, intentar deducirlo del monto
                from django.conf import settings
                monto_completo = getattr(settings, 'MONTO_TURNO_COMPLETO', 5000)
                monto_senia = getattr(settings, 'MONTO_SENIA', 1500)
                
                if turno.monto_pagado:
                    if float(turno.monto_pagado) >= monto_completo:
                        turno.pago_total = True
                        turno.tipo_pago = 'completo'
                    else:
                        turno.pago_senia = True
                        turno.tipo_pago = 'senia'
            
            turno.save()
            messages.success(request, '¡Pago procesado exitosamente!')
        
        context = {
            'turno': turno,
            'payment_id': payment_id
        }
        return render(request, 'pago_exitoso.html', context)
    
# class PagoExitosoView(LoginRequiredMixin, View):
#     """Vista cuando el pago fue exitoso"""
    
#     def get(self, request, turno_id):
#         turno = get_object_or_404(Turno, id=turno_id)
        
#         # Verificar que el turno pertenezca al usuario (excepto admin)
#         if not (request.user.is_superuser or request.user.is_staff):
#             if turno.usuario != request.user and turno.email != request.user.email:
#                 messages.error(request, 'No tienes permiso para ver este turno.')
#                 return redirect('lista_turnos')
        
#         payment_id = request.GET.get('payment_id')
        
#         if payment_id:
#             turno.payment_id = payment_id
#             turno.estado_pago = 'aprobado'
            
#             # Actualizar flags según tipo de pago
#             if turno.tipo_pago == 'completo':
#                 turno.pago_total = True
#             else:
#                 turno.pago_senia = True
            
#             turno.save()
        
#         context = {
#             'turno': turno,
#             'payment_id': payment_id
#         }
#         return render(request, 'pago_exitoso.html', context)


class PagoFallidoView(LoginRequiredMixin, View):
    """Vista cuando el pago falló"""
    
    def get(self, request, turno_id):
        turno = get_object_or_404(Turno, id=turno_id)
        
        # Verificar que el turno pertenezca al usuario (excepto admin)
        if not (request.user.is_superuser or request.user.is_staff):
            if turno.usuario != request.user and turno.email != request.user.email:
                messages.error(request, 'No tienes permiso para ver este turno.')
                return redirect('lista_turnos')
        
        turno.estado_pago = 'rechazado'
        turno.save()
        
        context = {'turno': turno}
        return render(request, 'pago_fallido.html', context)


class PagoPendienteView(LoginRequiredMixin, View):
    """Vista cuando el pago está pendiente"""
    
    def get(self, request, turno_id):
        turno = get_object_or_404(Turno, id=turno_id)
        
        # Verificar que el turno pertenezca al usuario (excepto admin)
        if not (request.user.is_superuser or request.user.is_staff):
            if turno.usuario != request.user and turno.email != request.user.email:
                messages.error(request, 'No tienes permiso para ver este turno.')
                return redirect('lista_turnos')
        
        turno.estado_pago = 'pendiente'
        turno.save()
        
        context = {'turno': turno}
        return render(request, 'pago_pendiente.html', context)


@method_decorator(csrf_exempt, name='dispatch')
class WebhookMercadoPagoView(View):
    """Webhook para recibir notificaciones de Mercado Pago"""
    
    def post(self, request):
        try:
            # Mercado Pago envía los datos en el body
            data = json.loads(request.body)
            
            # Verificar que sea una notificación de pago
            if data.get('type') == 'payment':
                payment_id = data['data']['id']
                
                # Obtener información del pago
                payment_info = verificar_pago(payment_id)
                
                if payment_info:
                    # Buscar el turno por external_reference
                    turno_id = payment_info.get('external_reference')
                    
                    if turno_id:
                        turno = Turno.objects.get(id=turno_id)
                        turno.payment_id = str(payment_id)
                        
                        # Actualizar estado según el status del pago
                        status = payment_info.get('status')
                        
                        if status == 'approved':
                            turno.estado_pago = 'aprobado'
                            if turno.tipo_pago == 'completo':
                                turno.pago_total = True
                            else:
                                turno.pago_senia = True
                        elif status == 'rejected':
                            turno.estado_pago = 'rechazado'
                        elif status in ['pending', 'in_process']:
                            turno.estado_pago = 'pendiente'
                        
                        turno.save()
            
            return HttpResponse(status=200)
            
        except Exception as e:
            print(f"Error en webhook: {str(e)}")
            return HttpResponse(status=400)


# EDITAR - Solo admin
class EditarTurno(LoginRequiredMixin, EsAdminMixin, UpdateView):
    model = Turno
    template_name = 'editar_turno.html'
    fields = ['fecha', 'paciente', 'dni', 'obrasocial', 'especialidad', 'estado_pago', 'activo']
    success_url = reverse_lazy('lista_turnos')


# ELIMINAR - Solo admin
class eliminarTurno(LoginRequiredMixin, EsAdminMixin, DeleteView):
    model = Turno
    success_url = reverse_lazy('lista_turnos')