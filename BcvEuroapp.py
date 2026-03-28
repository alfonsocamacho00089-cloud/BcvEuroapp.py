import requests
from bs4 import BeautifulSoup
import json
import os
import urllib3
import firebase_admin
from firebase_admin import credentials, messaging

# Desactivar advertencias de certificados
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuración de Firebase
service_account_info = json.loads(os.environ.get('FIREBASE_SERVICE_ACCOUNT'))
cred = credentials.Certificate(service_account_info)
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

def enviar_notificacion_precio(precio_dolar, precio_euro):
    message = messaging.Message(
        notification=messaging.Notification(
            title='¡BCV Actualizó! 🚀',
            body=f'Dólar: {precio_dolar} | Euro: {precio_euro}',
        ),
        topic='bcv_updates',
    )
    messaging.send(message)
    print("Notificación enviada con ambas tasas")

def capturar():
    url = "https://www.bcv.org.ve/tasas-informativas-sistema-bancario"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, verify=False, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        div_dolar = soup.find('div', id='dolar')
        div_euro = soup.find('div', id='euro')
        
        tasa_dolar = None
        tasa_euro = None

        if div_dolar:
            tasa_dolar = div_dolar.find('strong').get_text(strip=True).replace('.', '').replace(',', '.')
        
        if div_euro:
            tasa_euro = div_euro.find('strong').get_text(strip=True).replace('.', '').replace(',', '.')

        fecha_tag = soup.find('span', class_='date-display-single')
        fecha_valor = fecha_tag.get_text(strip=True) if fecha_tag else "Fecha no encontrada"

        if tasa_dolar and tasa_euro:
            # --- Lógica de historial (Dos posiciones) ---
            try:
                with open("Bcveuro.json", "r") as f:
                    historial = json.load(f)
                    if historial[0].get('precio_dolar') == tasa_dolar:
                        print(f"El precio {tasa_dolar} no ha cambiado.")
                        return 
                    tasa_vieja = historial[0]
            except:
                tasa_vieja = {"banco": "BCV", "precio_dolar": tasa_dolar, "precio_euro": tasa_euro, "fecha": fecha_valor}

            resultado = [
                {
                    "banco": "BCV Oficial",
                    "precio_dolar": tasa_dolar,
                    "precio_euro": tasa_euro,
                    "fecha": fecha_valor,
                    "estado": "proxima"
                },
                {
                    "banco": "BCV Oficial",
                    "precio_dolar": tasa_vieja.get('precio_dolar'),
                    "precio_euro": tasa_vieja.get('precio_euro'),
                    "fecha": tasa_vieja.get('fecha'),
                    "estado": "vigente"
                }
            ]

            with open("Bcveuro.json", "w") as f:
                json.dump(resultado, f, indent=4)
            
            print(f"¡Actualizado con éxito! Dólar: {tasa_dolar}")
            enviar_notificacion_precio(tasa_dolar, tasa_euro)
        else:
            print("No se pudieron capturar las tasas.")

    except Exception as e:
        print(f"Error en la captura: {e}")

if __name__ == "__main__":
    capturar()
