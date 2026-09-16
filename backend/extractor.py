import pdfplumber
import re
import json

def extraer_datos_completos_tda(ruta_pdf):
    jugadores_tda = []
    
    with pdfplumber.open(ruta_pdf) as pdf:
        texto_pagina = pdf.pages[0].extract_text()
        
        # Cortamos el texto para tomar solo la sección de TDA (antes de Envigado)
        if "Envigado" in texto_pagina:
            texto_tda = texto_pagina.split("Envigado")[0]
        else:
            texto_tda = texto_pagina

        # Patrón para capturar jugadoras con minutos jugados
        # Ejemplo: *4 MARIA BEDOYA 21:15 3/9 33.3 0/3 0,0 3/6 50,0 3/4 75.0 1 4 12 2 21 1 1 0 5 12
        patron_jugador = re.compile(
            r'(\*?\d+)\s+([A-Za-zÁÉÍÓÚáéíóúÑñ\s\(\)]+?)\s+(\d{2}:\d{2})\s+([\d/]+)\s+[\d,\.]+\s+([\d/]+)\s+[\d,\.]+\s+([\d/]+)\s+[\d,\.]+\s+([\d/]+)\s+[\d,\.]+\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(-?\d+)\s+(-?\d+)\s+(\d+)'
        )

        for linea in texto_tda.split("\n"):
            coincidencia = patron_jugador.search(linea)
            if coincidencia:
                g = coincidencia.groups()
                jugadores_tda.append({
                    "dorsal": g[0].replace("*", "").strip(),
                    "nombre": g[1].strip(),
                    "minutos": g[2],
                    "tiros_campo": g[3],
                    "tiros_2p": g[4],
                    "tiros_3p": g[5],
                    "tiros_libres": g[6],
                    "rebotes_ofensivos": int(g[7]),
                    "rebotes_defensivos": int(g[8]),
                    "asistencias": int(g[9]),
                    "perdidas": int(g[10]),
                    "robos": int(g[11]),
                    "tapones": int(g[12]),
                    "faltas_cometidas": int(g[13]),
                    "mas_menos": int(g[14]),
                    "eficiencia": int(g[15]),
                    "puntos": int(g[16]),
                    "jugo": True
                })
            elif "DNP" in linea and any(c.isdigit() for c in linea[:5]):
                # Jugadora que no jugó (DNP)
                partes = linea.split()
                jugadores_tda.append({
                    "dorsal": partes[0].replace("*", "").strip(),
                    "nombre": " ".join(partes[1:-1]),
                    "minutos": "00:00",
                    "tiros_campo": "0/0",
                    "tiros_2p": "0/0",
                    "tiros_3p": "0/0",
                    "tiros_libres": "0/0",
                    "rebotes_ofensivos": 0,
                    "rebotes_defensivos": 0,
                    "asistencias": 0,
                    "perdidas": 0,
                    "robos": 0,
                    "tapones": 0,
                    "faltas_cometidas": 0,
                    "mas_menos": 0,
                    "eficiencia": 0,
                    "puntos": 0,
                    "jugo": False
                })

    return jugadores_tda

if __name__ == "__main__":
    ruta_archivo = "uploads/partidoprueba.pdf"
    resultado = extraer_datos_completos_tda(ruta_archivo)
    print(json.dumps(resultado, indent=4, ensure_ascii=False))