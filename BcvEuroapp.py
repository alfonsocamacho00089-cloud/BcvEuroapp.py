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
        try:
            with open("Bcveuro.json", "r") as f:
                if json.load(f)[0].get('precio') == data.get('promedio'):
                    return # Si es igual, se sale y no hace nada más
        except:
            pass # Si el archivo no existe, sigue normal
        # ---------------------
       # st.metric(label="Precio Dólar BCV", value=data.get('promedio'))
        # Creamos una lista con el formato que necesitamos
        resultado = [{
            "banco": "BCV Oficial",
            "precio": data.get('promedio'),
            "fecha": data.get('fechaActualizacion')
        }]
        
        # Guardamos en el archivo
        with open("Bcveuro.json", "w") as f:
            json.dump(resultado, f, indent=4)
        print("¡LOGRADO!")
          # Buscamos el precio que acabas de obtener
        precio_bcv = data.get('promedio')
        # ¡Mandamos la notificación!
        enviar_notificacion_precio(precio_bcv)  
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    capturar()
