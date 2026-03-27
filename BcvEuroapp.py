import requests
import json

def capturar():
    
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
        st.metric(label="Precio Dólar BCV", value=data.get('promedio'))
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
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    capturar()
