import pdfplumber
import json

def extraer_datos_tda(ruta_pdf):
    jugadores_tda = []
    
    # Textos que queremos ignorar completamente por ser encabezados o basura
    palabras_basura = ["Name", "M/A", "%", "Totals", "Team/Coach", "Scoring", "Field", "Points", "Free", "Rebounds", "Fouls"]
    
    with pdfplumber.open(ruta_pdf) as pdf:
        pagina = pdf.pages[0]
        tablas = pagina.extract_tables()
        
        for tabla in tablas:
            # Verificamos si es la tabla de jugadoras (donde aparece MARIA BEDOYA)
            es_tabla_jugadores = any("MARIA BEDOYA" in str(fila) for fila in tabla)
            
            if es_tabla_jugadores:
                for fila in tabla:
                    # Unimos toda la fila como texto para validar filtros
                    texto_fila = " ".join([str(e) for e in fila if e is not None])
                    
                    # Ignoramos la fila si no tiene contenido o si contiene palabras clave de los encabezados
                    if not texto_fila.strip() or any(palabra in texto_fila for palabra in palabras_basura):
                        continue
                    
                    # Limpiamos los elementos individuales de la fila
                    fila_limpia = [str(elem).strip() for elem in fila if elem is not None and str(elem).strip() != ""]
                    
                    # Una fila válida de jugadora tiene al menos Dorsal, Nombre y Minutos
                    if len(fila_limpia) >= 3:
                        # Si llegamos a la sección del otro equipo (Envigado), paramos
                        if "Envigado" in fila_limpia[0] or "ENV" in fila_limpia[0]:
                            break
                        
                        # Extraemos los datos completos del Box Score
                        jugador = {
                            "dorsal": fila_limpia[0],
                            "nombre": fila_limpia[1],
                            "minutos": fila_limpia[2] if len(fila_limpia) > 2 else "00:00",
                            "puntos": fila_limpia[-1] if len(fila_limpia) > 0 else "0"
                        }
                        
                        # Solo agregamos si el dorsal no es un encabezado suelto
                        if jugador["dorsal"] not in ["No", "M/A", "%"]:
                            jugadores_tda.append(jugador)
                
                break

    return jugadores_tda

if __name__ == "__main__":
    ruta_archivo = "uploads/partidoprueba.pdf"
    resultado = extraer_datos_tda(ruta_archivo)
    print(json.dumps(resultado, indent=4, ensure_ascii=False))