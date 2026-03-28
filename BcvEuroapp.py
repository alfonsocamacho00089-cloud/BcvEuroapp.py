import requests
from bs4 import BeautifulSoup
import json
import os
import urllib3
import firebase_admin
from firebase_admin import credentials, messaging

# Desactivar advertencias de certificados (como en tu 2do código)
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
    # LA RUTA DIRECTA DEL SEGUNDO CÓDIGO
    url = "https://www.bcv.org.ve/tasas-informativas-sistema-bancario"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, verify=False, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Variables para guardar lo que encontremos
        tasa_dolar = None
        tasa_euro = None
        fecha_valor = ""

        # Buscamos en la tabla del BCV
        tabla = soup.find('table')
        if tabla:
            filas = tabla.find_all('tr')
            for fila in filas:
                celdas = fila.find_all('td')
                if len(celdas) >= 4:
                    moneda = celdas[1].get_text(strip=True)
                    valor = celdas[3].get_text(strip=True).replace('.', '').replace(',', '.')
                    fecha = celdas[0].get_text(strip=True)

                    if "USD" in moneda or "Dólar" in moneda:
                        tasa_dolar = valor
                        fecha_valor = fecha
                    elif "EUR" in moneda or "Euro" in moneda:
                        tasa_euro = valor

        if tasa_dolar and tasa_euro:
            # --- Lógica de no repetir (comparar con el archivo guardado) ---
            try:
                with open("Bcveuro.json", "r") as f:
                    contenido_previo = json.load(f)
                    # Comparamos el dólar para ver si hubo cambio
                    if contenido_previo[0].get('precio_dolar') == tasa_dolar:
                        print("El precio no ha cambiado en el BCV. Saliendo...")
                        return
            except:
                pass

            # Formato de resultado para tu JSON
            resultado = [{
                "banco": "BCV Oficial",
                "precio_dolar": tasa_dolar,
                "precio_euro": tasa_euro,
                "fecha": fecha_valor
            }]

            # Guardamos en el archivo
            with open("Bcveuro.json", "w") as f:
                json.dump(resultado, f, indent=4)
            
            print(f"¡LOGRADO! Dólar: {tasa_dolar}, Euro: {tasa_euro}")
            
            # Mandamos la notificación con las dos tasas
            enviar_notificacion_precio(tasa_dolar, tasa_euro)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    capturar()
