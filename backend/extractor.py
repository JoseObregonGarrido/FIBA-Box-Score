import pdfplumber
import json

def convertir_a_entero(valor):
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
            es_tabla_tda = any("MARIA BEDOYA" in str(fila) for fila in tabla)
            
            if es_tabla_tda:
                for fila in tabla:
                    fila_limpia = [str(e).strip() for e in fila if e is not None and str(e).strip() != ""]
                    texto_fila = " ".join(fila_limpia)
                    
                    if not fila_limpia or "Totals" in texto_fila or "Team/Coach" in texto_fila:
                        continue
                    
                    if "Envigado" in texto_fila or "ENV" in fila_limpia[0]:
                        break
                    
                    if len(fila_limpia) >= 3:
                        dorsal_raw = fila_limpia[0].replace("*", "").strip()
                        
                        # Validar que el dorsal sea numérico (elimina encabezados como M/A, No, %)
                        if not dorsal_raw.isdigit():
                            continue
                            
                        nombre = fila_limpia[1]
                        minutos = fila_limpia[2]
                        
                        if "DNP" in minutos:
                            jugadores_tda.append({
                                "dorsal": dorsal_raw,
                                "nombre": nombre,
                                "minutos": "00:00",
                                "puntos": 0,
                                "eficiencia": 0,
                                "jugo": False
                            })
                        else:
                            puntos = convertir_a_entero(fila_limpia[-1])
                            eficiencia = convertir_a_entero(fila_limpia[-2]) if len(fila_limpia) > 3 else 0
                            
                            jugadores_tda.append({
                                "dorsal": dorsal_raw,
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