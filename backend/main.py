import os
import shutil
from typing import List
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from extractor import extraer_datos_completos_tda

app = FastAPI(title="FIBA Box Score API - TDA")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/", response_class=HTMLResponse)
def leer_interfaz():
    ruta_html = os.path.join(os.path.dirname(__file__), "index.html")
    with open(ruta_html, "r", encoding="utf-8") as f:
        return f.read()

@app.post("/procesar-partidos/")
async def procesar_partidos(files: List[UploadFile] = File(...)):
    acumulado = {}
    total_partidos = len(files)

    for file in files:
        ruta_temporal = os.path.join(UPLOAD_DIR, file.filename)
        with open(ruta_temporal, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        datos = extraer_datos_completos_tda(ruta_temporal)
        
        for j in datos:
            nombre = j["nombre"]
            if nombre not in acumulado:
                acumulado[nombre] = {
                    "dorsal": j["dorsal"], "nombre": nombre, "pj": 0,
                    "pts": 0, "ro": 0, "rd": 0, "rt": 0, "as": 0, "to": 0,
                    "st": 0, "bs": 0, "pf": 0, "pm": 0, "ef": 0,
                    "tc_a": 0, "tc_i": 0, "t2_a": 0, "t2_i": 0,
                    "t3_a": 0, "t3_i": 0, "tl_a": 0, "tl_i": 0
                }
            
            if j["jugo"]:
                acumulado[nombre]["pj"] += 1
                for k in ["pts", "ro", "rd", "rt", "as", "to", "st", "bs", "pf", "pm", "ef", "tc_a", "tc_i", "t2_a", "t2_i", "t3_a", "t3_i", "tl_a", "tl_i"]:
                    acumulado[nombre][k] += j[k]

    res = []
    for j in acumulado.values():
        pj = j["pj"] if j["pj"] > 0 else 1
        res.append({
            "dorsal": j["dorsal"], "nombre": j["nombre"], "pj": j["pj"],
            "pts_tot": j["pts"], "pts_prom": round(j["pts"] / pj, 1),
            "tc": f"{j['tc_a']}/{j['tc_i']}", "tc_pct": round((j['tc_a']/j['tc_i']*100), 1) if j['tc_i'] > 0 else 0,
            "t2": f"{j['t2_a']}/{j['t2_i']}", "t3": f"{j['t3_a']}/{j['t3_i']}", "tl": f"{j['tl_a']}/{j['tl_i']}",
            "rt_tot": j["rt"], "rt_prom": round(j["rt"] / pj, 1),
            "as_tot": j["as"], "as_prom": round(j["as"] / pj, 1),
            "to_tot": j["to"], "st_tot": j["st"], "bs_tot": j["bs"],
            "pf_tot": j["pf"], "pm_tot": j["pm"], "ef_tot": j["ef"], "ef_prom": round(j["ef"] / pj, 1)
        })

    return {"partidos_procesados": total_partidos, "jugadoras": res}