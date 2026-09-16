import pdfplumber

def parse_int(val):
    try:
        clean_val = str(val).replace("*", "").strip()
        return int(clean_val)
    except (ValueError, TypeError):
        return 0

def parse_minutos(val):
    try:
        str_val = str(val).strip()
        if ":" in str_val:
            return int(str_val.split(":")[0])
        return int(str_val)
    except (ValueError, TypeError):
        return 0

def parse_intentos_convertidos(val):
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
        texto_completo = pagina.extract_text().upper()
        tablas = pagina.extract_tables()
        
        # 1. Determinamos si TDA es el Equipo 1 (Local) o Equipo 2 (Visitante)
        # Analizamos el orden en el texto del encabezado
        pos_tda = texto_completo.find("TECNOLOGICO")
        if pos_tda == -1:
            pos_tda = texto_completo.find("TDA")
            
        pos_vs = texto_completo.find(" VS ")
        if pos_vs == -1:
            pos_vs = texto_completo.find(" - ")

        # Si TDA aparece antes del 'VS' o '-', es la primera tabla (índice 0). Si aparece después, es la segunda (índice 1).
        indice_tabla_target = 0
        if pos_tda != -1 and pos_vs != -1 and pos_tda > pos_vs:
            indice_tabla_target = 1

        # 2. Si no se puede determinar por encabezado, buscamos qué tabla contiene números de dorsal válidos
        tablas_validas = []
        for tabla in tablas:
            filas_con_dorsal = 0
            for fila in tabla:
                if fila and str(fila[0]).replace("*", "").strip().isdigit():
                    filas_con_dorsal += 1
            if filas_con_dorsal >= 5: # Es una tabla de roster de jugadoras
                tablas_validas.append(tabla)

        if not tablas_validas:
            return []

        # Seleccionamos la tabla target basada en la posición
        tabla_tda = tablas_validas[min(indice_tabla_target, len(tablas_validas) - 1)]

        # 3. Extraemos las estadísticas independientemente de los nombres
        for fila in tabla_tda:
            fila_limpia = [str(e).strip() for e in fila if e is not None and str(e).strip() != ""]
            texto_fila = " ".join(fila_limpia).upper()
            
            if not fila_limpia or "TOTALS" in texto_fila or "TOTALES" in texto_fila or "TEAM/COACH" in texto_fila or "EQUIPO/ENTRENADOR" in texto_fila:
                continue
                
            if len(fila_limpia) >= 3:
                dorsal_raw = fila_limpia[0].replace("*", "").strip()
                if not dorsal_raw.isdigit():
                    continue
                    
                nombre = fila_limpia[1]
                min_raw = fila_limpia[2]
                
                if "DNP" in min_raw.upper() or "NJ" in min_raw.upper() or "NE" in min_raw.upper():
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
                        "fd": parse_int(fila_limpia[-4]) if len(fila_limpia) >= 4 else 0,
                        "pf": parse_int(fila_limpia[-5]) if len(fila_limpia) >= 5 else 0,
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

    return jugadores_tda