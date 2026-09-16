import pdfplumber
import json

def limpiar_dorsal(dorsal_raw):
    """Limpia el asterisco de titular si lo tiene."""
    return dorsal_raw.replace("*", "").strip()

def extraer_datos_completos_tda(ruta_pdf):
    jugadores_tda = []
    
    palabras_basura = ["Name", "M/A", "%", "Totals", "Team/Coach", "Scoring", "Field", "Points", "Free", "Rebounds", "Fouls"]
    
    with pdfplumber.open(ruta_pdf) as pdf:
        pagina = pdf.pages[0]
        tabla = pagina.extract_tables()[0]  # La primera tabla principal contiene TDA
        
        for fila in tabla:
            texto_fila = " ".join([str(e) for e in fila if e is not None])
            
            # Filtro de encabezados
            if not texto_fila.strip() or any(palabra in texto_fila for palabra in palabras_basura):
                continue
                
            fila_limpia = [str(elem).strip() for elem in fila if elem is not None and str(elem).strip() != ""]
            
            # Si entramos a la sección de Envigado, frenamos
            if "Envigado" in texto_fila or "ENV" in fila_limpia[0]:
                break
                
            if len(fila_limpia) >= 3:
                dorsal = limpiar_dorsal(fila_limpia[0])
                nombre = fila_limpia[1]
                minutos = fila_limpia[2]
                
                # Caso de jugadora que no jugó
                if "DNP" in minutos:
                    jugador = {
                        "dorsal": dorsal,
                        "nombre": nombre,
                        "minutos": "00:00",
                        "puntos": 0,
                        "rebotes_totales": 0,
                        "asistencias": 0,
                        "perdidas": 0,
                        "robos": 0,
                        "bloqueos": 0,
                        "eficiencia": 0,
                        "jugo": False
                    }
                else:
                    # Parseo dinámico según posición de columnas
                    jugador = {
                        "dorsal": dorsal,
                        "nombre": nombre,
                        "minutos": minutos,
                        "puntos": int(fila_limpia[-1]) if fila_limpia[-1].isdigit() else 0,
                        "eficiencia": int(fila_limpia[-2]) if len(fila_limpia) > 3 and fila_limpia[-2].lstrip('-').isdigit() else 0,
                        "jugo": True
                    }
                
                if dorsal.isdigit():
                    jugadores_tda.append(jugador)

    return jugadores_tda

if __name__ == "__main__":
    ruta_archivo = "uploads/partidoprueba.pdf"
    resultado = extraer_datos_completos_tda(ruta_archivo)
    print(json.dumps(resultado, indent=4, ensure_ascii=False))