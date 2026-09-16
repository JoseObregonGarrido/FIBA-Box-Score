import pdfplumber

def parse_int(val):
    try:
        # Remueve asteriscos de titularidad y espacios
        clean_val = str(val).replace("*", "").strip()
        return int(clean_val)
    except (ValueError, TypeError):
        return 0

def parse_intentos_convertidos(val):
    """Extrae convertidos e intentados de cadenas tipo '3/9' o '0/0'"""
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
            # Detectamos si es la tabla de TDA
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
                        
                        # Si no jugó (DNP)
                        if "DNP" in minutos:
                            jugadores_tda.append({
                                "dorsal": dorsal_raw, 
                                "nombre": nombre, 
                                "jugo": False,
                                "pts": 0, "ef": 0, "pm": 0, "pf": 0, "bs": 0,
                                "st": 0, "to": 0, "as": 0, "rt": 0, "rd": 0, "ro": 0,
                                "tc_a": 0, "tc_i": 0, "t2_a": 0, "t2_i": 0,
                                "t3_a": 0, "t3_i": 0, "tl_a": 0, "tl_i": 0
                            })
                        else:
                            tc_a, tc_i = parse_intentos_convertidos(fila_limpia[3]) if len(fila_limpia) > 3 else (0,0)
                            t2_a, t2_i = parse_intentos_convertidos(fila_limpia[5]) if len(fila_limpia) > 5 else (0,0)
                            t3_a, t3_i = parse_intentos_convertidos(fila_limpia[7]) if len(fila_limpia) > 7 else (0,0)
                            tl_a, tl_i = parse_intentos_convertidos(fila_limpia[9]) if len(fila_limpia) > 9 else (0,0)

                            jugadores_tda.append({
                                "dorsal": dorsal_raw,
                                "nombre": nombre,
                                "jugo": True,
                                "pts": parse_int(fila_limpia[-1]),
                                "ef": parse_int(fila_limpia[-2]) if len(fila_limpia) >= 2 else 0,
                                "pm": parse_int(fila_limpia[-3]) if len(fila_limpia) >= 3 else 0,
                                "pf": parse_int(fila_limpia[-4]) if len(fila_limpia) >= 4 else 0,
                                "bs": parse_int(fila_limpia[-5]) if len(fila_limpia) >= 5 else 0,
                                "st": parse_int(fila_limpia[-6]) if len(fila_limpia) >= 6 else 0,
                                "to": parse_int(fila_limpia[-7]) if len(fila_limpia) >= 7 else 0,
                                "as": parse_int(fila_limpia[-8]) if len(fila_limpia) >= 8 else 0,
                                "rt": parse_int(fila_limpia[-9]) if len(fila_limpia) >= 9 else 0,
                                "rd": parse_int(fila_limpia[-10]) if len(fila_limpia) >= 10 else 0,
                                "ro": parse_int(fila_limpia[-11]) if len(fila_limpia) >= 11 else 0,
                                "tc_a": tc_a, "tc_i": tc_i,
                                "t2_a": t2_a, "t2_i": t2_i,
                                "t3_a": t3_a, "t3_i": t3_i,
                                "tl_a": tl_a, "tl_i": tl_i,
                            })
                break
    return jugadores_tda