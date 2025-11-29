import mercadopago
from django.conf import settings
from django.urls import reverse

def crear_preferencia_pago(turno, tipo_pago, request):
    try:
        sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
        
        # Debug
        print(f"=== DEBUG CREAR PREFERENCIA ===")
        print(f"Turno ID: {turno.id}")
        print(f"Turno PK: {turno.pk}")
        print(f"Tipo pago: {tipo_pago}")
        
        # Determinar el monto según el tipo de pago
        if tipo_pago == 'completo':
            monto = float(settings.MONTO_TURNO_COMPLETO)
            titulo = f"Turno Completo - {turno.especialidad.tipo}"
            descripcion = f"Pago completo del turno para {turno.paciente}"
        else:  # seña
            monto = float(settings.MONTO_SENIA)
            titulo = f"Seña de Turno - {turno.especialidad.tipo}"
            descripcion = f"Seña del turno para {turno.paciente}"
        
        # Construir URLs absolutas usando pk en lugar de id
        turno_id = turno.pk if turno.pk else turno.id
        print(f"Usando turno_id: {turno_id}")
        
        success_url = request.build_absolute_uri(reverse('pago_exitoso', args=[turno_id]))
        failure_url = request.build_absolute_uri(reverse('pago_fallido', args=[turno_id]))
        pending_url = request.build_absolute_uri(reverse('pago_pendiente', args=[turno_id]))
        
        print(f"Success URL: {success_url}")
        
        # Crear la preferencia
        preference_data = {
            "items": [
                {
                    "title": titulo,
                    "description": descripcion,
                    "quantity": 1,
                    "unit_price": monto,
                    "currency_id": "ARS"
                }
            ],
            "payer": {
                "name": turno.paciente,
                "email": turno.email if turno.email else "test@test.com",

                "identification": {
                    "type": "DNI",
                    "number": str(turno.dni)
                }
            },
            "back_urls": {
                "success": success_url,
                "failure": failure_url,
                "pending": pending_url
            },
            # Quitamos auto_return para desarrollo en localhost
            # "auto_return": "all",
            "external_reference": str(turno_id),
            "statement_descriptor": "CONSULTORIO MEDICO",
            "metadata": {
                "turno_id": turno_id,
                "tipo_pago": tipo_pago
            }
        }
        
        print(f"Preference data: {preference_data}")
        
        # Crear preferencia en Mercado Pago
        preference_response = sdk.preference().create(preference_data)
        
        print(f"=== RESPUESTA DE MERCADO PAGO ===")
        print(f"Status: {preference_response.get('status')}")
        print(f"Response completa: {preference_response}")
        
        # Verificar si hubo error
        if preference_response.get("status") != 201:
            error_message = preference_response.get("response", {})
            print(f"ERROR DE MERCADO PAGO: {error_message}")
            raise Exception(f"Error de Mercado Pago: {error_message}")
        
        preference = preference_response["response"]
        
        print(f"Preferencia creada: {preference['id']}")
        
        return {
            "preference_id": preference["id"],
            "init_point": preference["init_point"],  # URL para web
            "sandbox_init_point": preference.get("sandbox_init_point", "")  # URL para pruebas
        }
    except Exception as e:
        import traceback
        print(f"ERROR EN CREAR PREFERENCIA:")
        print(traceback.format_exc())
        raise e


def verificar_pago(payment_id):

    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
    payment_info = sdk.payment().get(payment_id)
    
    if payment_info["status"] == 200:
        return payment_info["response"]
    return None