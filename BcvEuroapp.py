import requests
import json
import os
import firebase_admin
from firebase_admin import credentials, messaging

# Configuración de Firebase
service_account_info = json.loads(os.environ.get('FIREBASE_SERVICE_ACCOUNT'))
cred = credentials.Certificate(service_account_info)
firebase_admin.initialize_app(cred)
def enviar_notificacion_precio(nuevo_precio):
    message = messaging.Message(
        notification=messaging.Notification(
            title='¡El BCV Actualizó! 🚀',
            body=f'El nuevo precio oficial es: {nuevo_precio} Bs.',
        ),
        topic='bcv_updates',
    )
    messaging.send(message)
    print("Notificación enviada a los usuarios.")

def capturar():
    # ... aquí sigue el resto de tu código ...
    
    # Esta es la URL más estable ahorita para el BCV
    url = "https://ve.dolarapi.com/v1/dolares/oficial"
    
    try:
        response = requests.get(url, timeout=20)
        data = response.json()
    # --- AGREGAR ESTO ---
        precio_bcv = data.get('promedio')
        fecha_bcv = data.get('fechaActualizacion')

        try:
            with open("Bcveuro.json", "r") as f:
                datos_viejos = json.load(f)
                if datos_viejos[0].get('precio') == precio_bcv:
                    print("El BCV no ha cambiado. Abortando misión.")
                    return
        except:
            pass

        resultado = [{
            "banco": "BCV Oficial",
            "precio": precio_bcv,
            "fecha": fecha_bcv
        }]

        with open("Bcveuro.json", "w") as f:
            json.dump(resultado, f, indent=4)
            
        print("¡LOGRADO! Precio nuevo detectado.")
        enviar_notificacion_precio(precio_bcv)        

        if __name__ == "__main__":
        capturar()
