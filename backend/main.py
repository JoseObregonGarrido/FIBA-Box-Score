from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import shutil
import os

from extractor import extraer_datos_completos_tda

app = FastAPI(title="FIBA Box Score API - TDA")

# Permitir peticiones desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def home():
    return {"message": "API FIBA Box Score TDA funcionando correctamente"}

@app.post("/procesar-partidos/")
async def procesar_partidos(files: List[UploadFile] = File(...)):
    acumulado_jugadoras = {}
    total_partidos = len(files)

    for file in files:
        ruta_temporal = os.path.join(UPLOAD_DIR, file.filename)
        
        # Guardar archivo localmente en uploads/
        with open(ruta_temporal, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Extraer datos de TDA para este PDF
        datos_partido = extraer_datos_completos_tda(ruta_temporal)
        
        # Consolidar estadísticas
        for jugadora in datos_partido:
            nombre = jugadora["nombre"]
            
            if nombre not in acumulado_jugadoras:
                acumulado_jugadoras[nombre] = {
                    "dorsal": jugadora["dorsal"],
                    "nombre": nombre,
                    "partidos_jugados": 0,
                    "puntos_totales": 0,
                    "eficiencia_total": 0
                }
            
            if jugadora["jugo"]:
                acumulado_jugadoras[nombre]["partidos_jugados"] += 1
                acumulado_jugadoras[nombre]["puntos_totales"] += jugadora["puntos"]
                acumulado_jugadoras[nombre]["eficiencia_total"] += jugadora["eficiencia"]

    # Calculemos los promedios generales
    estadisticas_generales = []
    for jugadora in acumulado_jugadoras.values():
        pj = jugadora["partidos_jugados"]
        estadisticas_generales.append({
            "dorsal": jugadora["dorsal"],
            "nombre": jugadora["nombre"],
            "partidos_jugados": pj,
            "puntos_totales": jugadora["puntos_totales"],
            "promedio_puntos": round(jugadora["puntos_totales"] / pj, 2) if pj > 0 else 0,
            "eficiencia_total": jugadora["eficiencia_total"],
            "promedio_eficiencia": round(jugadora["eficiencia_total"] / pj, 2) if pj > 0 else 0
        })

    return {
        "partidos_procesados": total_partidos,
        "jugadoras": estadisticas_generales
    }