import pdfplumber
import json

def convertir_a_entero(valor):
    """Convierte un valor a entero de forma segura."""
    try:
        return int(valor)
    except (ValueError, TypeError):
        return 0

def extraer_datos_completos_tda(ruta_pdf):
    jugadores_tda = []
    
    with pdfplumber.open(ruta_pdf) as pdf:
        pagina = pdf.pages[0]
        tablas = pagina.extract_tables()
        
        for tabla in tablas:
            # Buscamos la tabla que contenga jugadoras de TDA
            es_tabla_tda = any("MARIA BEDOYA" in str(fila) for fila in tabla)
            
            if es_tabla_tda:
                for fila in tabla:
                    # Limpiamos elementos nulos
                    fila_limpia = [str(e).strip() for e in fila if e is not None and str(e).strip() != ""]
                    
                    texto_fila = " ".join(fila_limpia)
                    
                    # Ignoramos encabezados y totales
                    if not fila_limpia or "Name" in texto_fila or "Totals" in texto_fila or "Team/Coach" in texto_fila:
                        continue
                    
                    # Si llegamos a Envigado, detenemos la lectura
                    if "Envigado" in texto_fila or "ENV" in fila_limpia[0]:
                        break
                    
                    if len(fila_limpia) >= 3:
                        dorsal = fila_limpia[0].replace("*", "").strip()
                        nombre = fila_limpia[1]
                        minutos = fila_limpia[2]
                        
                        # Manejo de jugadoras que no jugaron
                        if "DNP" in minutos:
                            jugadores_tda.append({
                                "dorsal": dorsal,
                                "nombre": nombre,
                                "minutos": "00:00",
                                "puntos": 0,
                                "eficiencia": 0,
                                "jugo": False
                            })
                        else:
                            # Tomamos los puntos (última columna) y eficiencia (penúltima)
                            puntos = convertir_a_entero(fila_limpia[-1])
                            eficiencia = convertir_a_entero(fila_limpia[-2]) if len(fila_limpia) > 3 else 0
                            
                            jugadores_tda.append({
                                "dorsal": dorsal,
                                "nombre": nombre,
                                "minutos": minutos,
                                "puntos": puntos,
                                "eficiencia": eficiencia,
                                "jugo": True
                            })
                break

    return jugadores_tda

if __name__ == "__main__":
    ruta_archivo = "uploads/partidoprueba.pdf"
    resultado = extraer_datos_completos_tda(ruta_archivo)
    print(json.dumps(resultado, indent=4, ensure_ascii=False))