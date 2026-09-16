import pdfplumber
import json

def parse_int(val):
    try:
        return int(str(val).replace("*", "").strip())
    except (ValueError, TypeError):
        return 0

def parse_intentos_convertidos(val):
    """Saca anotados e intentados de formatos como '3/9'"""
    try:
        partes = str(val).split('/')
        if len(partes) == 2:
            return int(partes[0]), int(partes[1])
    except Exception:
        pass
    return 0, 0

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
                        if not dorsal_raw.isdigit():
                            continue
                            
                        nombre = fila_limpia[1]
                        minutos = fila_limpia[2]
                        
                        if "DNP" in minutos:
                            jugadores_tda.append({
                                "dorsal": dorsal_raw, "nombre": nombre, "jugo": False,
                                "puntos": 0, "tc_a": 0, "tc_i": 0, "t2_a": 0, "t2_i": 0,
                                "t3_a": 0, "t3_i": 0, "tl_a": 0, "tl_i": 0, "ro": 0, "rd": 0,
                                "rt": 0, "as": 0, "to": 0, "st": 0, "bs": 0, "pf": 0, "pm": 0, "ef": 0
                            })
                        else:
                            # Posiciones relativas estándar en tabla FIBA limpia
                            # [0:No, 1:Name, 2:Min, 3:TC, 4:%, 5:2P, 6:%, 7:3P, 8:%, 9:TL, 10:%, 11:RO, 12:RD, 13:RT, 14:AS, 15:TO, 16:ST, 17:BS, 18:PF, 19:+/-, 20:EF, 21:PTS]
                            tc_a, tc_i = parse_intentos_convertidos(fila_limpia[3]) if len(fila_limpia) > 3 else (0,0)
                            t2_a, t2_i = parse_intentos_convertidos(fila_limpia[5]) if len(fila_limpia) > 5 else (0,0)
                            t3_a, t3_i = parse_intentos_convertidos(fila_limpia[7]) if len(fila_limpia) > 7 else (0,0)
                            tl_a, tl_i = parse_intentos_convertidos(fila_limpia[9]) if len(fila_limpia) > 9 else (0,0)

                            jugadores_tda.append({
                                "dorsal": dorsal_raw,
                                "nombre": nombre,
                                "jugo": True,
                                "puntos": parse_int(fila_limpia[-1]),
                                "ef": parse_int(fila_limpia[-2]) if len(fila_limpia) > 20 else 0,
                                "pm": parse_int(fila_limpia[-3]) if len(fila_limpia) > 19 else 0,
                                "pf": parse_int(fila_limpia[-4]) if len(fila_limpia) > 18 else 0,
                                "bs": parse_int(fila_limpia[-5]) if len(fila_limpia) > 17 else 0,
                                "st": parse_int(fila_limpia[-6]) if len(fila_limpia) > 16 else 0,
                                "to": parse_int(fila_limpia[-7]) if len(fila_limpia) > 15 else 0,
                                "as": parse_int(fila_limpia[-8]) if len(fila_limpia) > 14 else 0,
                                "rt": parse_int(fila_limpia[-9]) if len(fila_limpia) > 13 else 0,
                                "rd": parse_int(fila_limpia[-10]) if len(fila_limpia) > 12 else 0,
                                "ro": parse_int(fila_limpia[-11]) if len(fila_limpia) > 11 else 0,
                                "tc_a": tc_a, "tc_i": tc_i,
                                "t2_a": t2_a, "t2_i": t2_i,
                                "t3_a": t3_a, "t3_i": t3_i,
                                "tl_a": tl_a, "tl_i": tl_i,
                            })
                break
    return jugadores_tda