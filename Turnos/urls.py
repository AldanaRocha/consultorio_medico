from django.urls import path
from .views import (
    listaTurnos, 
    CrearTurno, 
    EditarTurno, 
    eliminarTurno,
    SeleccionarPagoView,
    PagoExitosoView,
    PagoFallidoView,
    PagoPendienteView,
    WebhookMercadoPagoView
)

urlpatterns = [
    path('', listaTurnos.as_view(), name='lista_turnos'),
    path('nuevo/', CrearTurno.as_view(), name='crear_turno'),
    path('<int:pk>/editar/', EditarTurno.as_view(), name='editar_turno'),
    path('<int:pk>/eliminar/', eliminarTurno.as_view(), name='eliminar_turno'),
    
    # URLs de pago
    path('pago/<int:turno_id>/', SeleccionarPagoView.as_view(), name='seleccionar_pago'),
    path('pago/exitoso/<int:turno_id>/', PagoExitosoView.as_view(), name='pago_exitoso'),
    path('pago/fallido/<int:turno_id>/', PagoFallidoView.as_view(), name='pago_fallido'),
    path('pago/pendiente/<int:turno_id>/', PagoPendienteView.as_view(), name='pago_pendiente'),
    
    # Webhook de Mercado Pago
    path('webhook/mercadopago/', WebhookMercadoPagoView.as_view(), name='webhook_mercadopago'),
]