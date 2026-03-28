import requests
import json
import os
import firebase_admin
from firebase_admin import credentials, messaging

# Configuración de Firebase - AHORA COINCIDE CON TU GITHUB ACTION
service_account_info = json.loads(os.environ.get('FIREBASE_SERVICE_ACCOUNT'))
cred = credentials.Certificate(service_account_info)
firebase_admin.initialize_app(cred)

def enviar_notificacion_precio(nuevo_precio):
    message = messaging.Message(
        notification=messaging.Notification(
            title='¡El BCV Actualizó! 🚀',
            body=f'El nuevo precio oficial es: {nuevo_precio}',
        ),
        topic='bcv_updates',
    )
    messaging.send(message)
    print("Notificación enviada a los usuarios")

def capturar():
    # Esta es la URL más estable ahorita para el dolar oficial
    url = "https://ve.dolarapi.com/v1/dolares/oficial"

    try:
        response = requests.get(url, timeout=20)
        data = response.json()
        
        # --- Lógica para no repetir si el precio es el mismo ---
        try:
            with open("Bcveuro.json", "r") as f:
                contenido = json.load(f)
                if contenido[0].get('precio') == data.get('promedio'):
                    print("El precio no ha cambiado. Saliendo...")
                    return 
        except:
            pass 

        # Formato de resultado
        resultado = [{
            "banco": "BCV Oficial",
            "precio": data.get('promedio'),
            "fecha": data.get('fechaActualizacion')
        }]

        # Guardamos en el archivo
        with open("Bcveuro.json", "w") as f:
            json.dump(resultado, f, indent=4)
        
        print("¡LOGRADO!")
        
        # Mandamos la notificación
        precio_bcv = data.get('promedio')
        enviar_notificacion_precio(precio_bcv)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    capturar()
