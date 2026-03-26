import requests
import json

def capturar():
    # Esta es la URL más estable ahorita para el BCV
    url = "https://ve.dolarapi.com/v1/dolares/oficial"
    
    try:
        response = requests.get(url, timeout=20)
        data = response.json()
        
        # Creamos una lista con el formato que necesitamos
        resultado = [{
            "banco": "BCV Oficial",
            "precio": data.get('actualizada'),
            "fecha": data.get('fechaActualizacion')
        }]
        
        # Guardamos en el archivo
        with open("bcveuro.json", "w") as f:
            json.dump(resultado, f, indent=4)
        print("¡LOGRADO!")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    capturar()
