import pdfplumber

def parse_int(val):
    try:
        return int(str(val).replace("*", "").strip())
    except (ValueError, TypeError):
        return 0

def parse_minutos(val):
    """Extrae minutos numéricos ignorando segundos si los hay (ej: '25:30' -> 25)"""
    try:
        str_val = str(val).strip()
        if ":" in str_val:
            return int(str_val.split(":")[0])
        return int(str_val)
    except (ValueError, TypeError):
        return 0

def parse_intentos_convertidos(val):
    """Separa convertidos e intentados de formatos tipo '3/9'"""
    try:
        partes = str(val).split('/')
        if len(partes) == 2:
            return parse_int(partes[0]), parse_int(partes[1])
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
                        min_raw = fila_limpia[2]
                        
                        if "DNP" in min_raw:
                            jugadores_tda.append({
                                "dorsal": dorsal_raw, "nombre": nombre, "jugo": False,
                                "min": 0, "pts": 0, "fgm": 0, "fga": 0, "m2": 0, "a2": 0,
                                "m3": 0, "a3": 0, "ftm": 0, "fta": 0, "ro": 0, "rd": 0,
                                "rt": 0, "as": 0, "to": 0, "st": 0, "bs": 0, "pf": 0,
                                "fd": 0, "pm": 0, "ef": 0
                            })
                        else:
                            fgm, fga = parse_intentos_convertidos(fila_limpia[3]) if len(fila_limpia) > 3 else (0,0)
                            m2, a2 = parse_intentos_convertidos(fila_limpia[5]) if len(fila_limpia) > 5 else (0,0)
                            m3, a3 = parse_intentos_convertidos(fila_limpia[7]) if len(fila_limpia) > 7 else (0,0)
                            ftm, fta = parse_intentos_convertidos(fila_limpia[9]) if len(fila_limpia) > 9 else (0,0)

                            jugadores_tda.append({
                                "dorsal": dorsal_raw,
                                "nombre": nombre,
                                "jugo": True,
                                "min": parse_minutos(min_raw),
                                "pts": parse_int(fila_limpia[-1]),
                                "ef": parse_int(fila_limpia[-2]) if len(fila_limpia) >= 2 else 0,
                                "pm": parse_int(fila_limpia[-3]) if len(fila_limpia) >= 3 else 0,
                                "fd": parse_int(fila_limpia[-4]) if len(fila_limpia) >= 4 else 0, # Faltas Recibidas
                                "pf": parse_int(fila_limpia[-5]) if len(fila_limpia) >= 5 else 0, # Faltas Cometidas
                                "bs": parse_int(fila_limpia[-6]) if len(fila_limpia) >= 6 else 0,
                                "st": parse_int(fila_limpia[-7]) if len(fila_limpia) >= 7 else 0,
                                "to": parse_int(fila_limpia[-8]) if len(fila_limpia) >= 8 else 0,
                                "as": parse_int(fila_limpia[-9]) if len(fila_limpia) >= 9 else 0,
                                "rt": parse_int(fila_limpia[-10]) if len(fila_limpia) >= 10 else 0,
                                "rd": parse_int(fila_limpia[-11]) if len(fila_limpia) >= 11 else 0,
                                "ro": parse_int(fila_limpia[-12]) if len(fila_limpia) >= 12 else 0,
                                "fgm": fgm, "fga": fga,
                                "m2": m2, "a2": a2,
                                "m3": m3, "a3": a3,
                                "ftm": ftm, "fta": fta
                            })
                break
    return jugadores_tda