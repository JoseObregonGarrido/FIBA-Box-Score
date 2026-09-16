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
            dorsal = j["dorsal"]
            
            if dorsal not in acumulado:
                acumulado[dorsal] = {
                    "dorsal": dorsal, 
                    "nombre": j["nombre"], 
                    "pj": 0,
                    "min": 0, "pts": 0, "fgm": 0, "fga": 0, "m2": 0, "a2": 0,
                    "m3": 0, "a3": 0, "ftm": 0, "fta": 0, "ro": 0, "rd": 0,
                    "rt": 0, "as": 0, "to": 0, "st": 0, "bs": 0, "pf": 0,
                    "fd": 0, "pm": 0, "ef": 0
                }
            else:
                if len(j["nombre"]) > len(acumulado[dorsal]["nombre"]):
                    acumulado[dorsal]["nombre"] = j["nombre"]
            
            if j["jugo"]:
                acumulado[dorsal]["pj"] += 1
                for k in ["min", "pts", "fgm", "fga", "m2", "a2", "m3", "a3", "ftm", "fta", 
                          "ro", "rd", "rt", "as", "to", "st", "bs", "pf", "fd", "pm", "ef"]:
                    acumulado[dorsal][k] += j.get(k, 0)

    res = []
    for dorsal in sorted(acumulado.keys(), key=lambda x: int(x) if x.isdigit() else 99):
        j = acumulado[dorsal]
        pj = j["pj"] if j["pj"] > 0 else 1
        
        fg_pct = round((j["fgm"] / j["fga"] * 100), 1) if j["fga"] > 0 else 0
        p2_pct = round((j["m2"] / j["a2"] * 100), 1) if j["a2"] > 0 else 0
        p3_pct = round((j["m3"] / j["a3"] * 100), 1) if j["a3"] > 0 else 0
        ft_pct = round((j["ftm"] / j["fta"] * 100), 1) if j["fta"] > 0 else 0

        res.append({
            "dorsal": j["dorsal"],
            "nombre": j["nombre"],
            "pj": j["pj"],
            "min_tot": j["min"],
            "min_prom": round(j["min"] / pj, 1),
            "pts_tot": j["pts"],
            "pts_prom": round(j["pts"] / pj, 1),
            "fgm": j["fgm"], "fga": j["fga"], "fg_pct": fg_pct,
            "m2": j["m2"], "a2": j["a2"], "p2_pct": p2_pct,
            "m3": j["m3"], "a3": j["a3"], "p3_pct": p3_pct,
            "ftm": j["ftm"], "fta": j["fta"], "ft_pct": ft_pct,
            "ro": j["ro"], "rd": j["rd"],
            "rt_tot": j["rt"], "rt_prom": round(j["rt"] / pj, 1),
            "as_tot": j["as"], "as_prom": round(j["as"] / pj, 1),
            "to_tot": j["to"], "to_prom": round(j["to"] / pj, 1),
            "st_tot": j["st"], "st_prom": round(j["st"] / pj, 1),
            "bs_tot": j["bs"], "bs_prom": round(j["bs"] / pj, 1),
            "pf_tot": j["pf"],
            "fd_tot": j["fd"],
            "pm_tot": j["pm"], "pm_prom": round(j["pm"] / pj, 1),
            "ef_tot": j["ef"], "ef_prom": round(j["ef"] / pj, 1)
        })

    return {"partidos_procesados": total_partidos, "jugadoras": res}