import pdfplumber
import json

def extraer_datos_tda(ruta_pdf):
    jugadores_tda = []
    
    with pdfplumber.open(ruta_pdf) as pdf:
        pagina = pdf.pages[0]
        tablas = pagina.extract_tables()
        
        for tabla in tablas:
            # Buscamos si esta tabla corresponde al plantel de jugadoras
            es_tabla_jugadores = any("MARIA BEDOYA" in str(fila) for fila in tabla)
            
            if es_tabla_jugadores:
                for fila in tabla:
                    # Filtramos elementos vacíos
                    fila_limpia = [str(elem).strip() for elem in fila if elem is not None and str(elem).strip() != ""]
                    
                    # Ignoramos encabezados o filas de totales
                    if not fila_limpia or "Name" in fila_limpia or "Totals" in fila_limpia or "Team/Coach" in fila_limpia:
                        continue
                    
                    # Estructura típica de jugadora TDA: ['*4', 'MARIA BEDOYA', '21:15', ...]
                    if len(fila_limpia) >= 3:
                        # Si encontramos la fila de Envigado o un corte, detenemos
                        if "Envigado" in fila_limpia[0] or "ENV" in fila_limpia[0]:
                            break
                            
                        jugador = {
                            "dorsal": fila_limpia[0],
                            "nombre": fila_limpia[1],
                            "minutos": fila_limpia[2] if len(fila_limpia) > 2 else "",
                            "puntos": fila_limpia[-1] if len(fila_limpia) > 0 else "0"
                        }
                        jugadores_tda.append(jugador)
                
                # Al terminar la tabla de TDA, salimos del ciclo
                break

    return jugadores_tda

if __name__ == "__main__":
    ruta_archivo = "uploads/partidoprueba.pdf"
    resultado = extraer_datos_tda(ruta_archivo)
    print(json.dumps(resultado, indent=4, ensure_ascii=False))