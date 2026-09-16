import pdfplumber
import json

def extraer_datos_tda(ruta_pdf):
    jugadores_tda = []
    
    with pdfplumber.open(ruta_pdf) as pdf:
        pagina = pdf.pages[0]
        tablas = pagina.extract_tables()
        
        # Iteramos sobre las tablas para encontrar la de TDA
        for tabla in tablas:
            for fila in tabla:
                # Limpiamos los valores de la fila
                fila_limpia = [elem.strip() if elem else "" for elem in fila]
                
                # Descartamos encabezados, filas vacías o la fila de totales
                if not fila_limpia or "Name" in fila_limpia or "Totals" in fila_limpia:
                    continue
                
                # Verificamos si la fila contiene datos de un jugador (dorsal + nombre)
                # Ejemplo de fila: ['*4', 'MARIA BEDOYA', '21:15', '3/9', ...]
                if len(fila_limpia) > 2 and fila_limpia[1] != "":
                    # Guardamos la estructura del jugador
                    jugador = {
                        "dorsal": fila_limpia[0],
                        "nombre": fila_limpia[1],
                        "minutos": fila_limpia[2] if len(fila_limpia) > 2 else "",
                        "puntos": fila_limpia[-1] if len(fila_limpia) > 0 else ""
                    }
                    jugadores_tda.append(jugador)
            
            # Una vez procesamos la primera tabla de jugadoras (TDA), detenemos para no leer Envigado
            if jugadores_tda:
                break

    return jugadores_tda

if __name__ == "__main__":
    # Nombre exacto del archivo que tienes dentro de backend/uploads
    ruta_archivo = "uploads/partidoprueba.pdf"
    resultado = extraer_datos_tda(ruta_archivo)
    print(json.dumps(resultado, indent=4, ensure_ascii=False))