from fastapi import FastAPI, HTTPException, BackgroundTasks
from uuid import uuid4
from datetime import datetime
from app.models.request_models import ProcessRequest
from app.services.download_service import start_download_stage
from app.services.resize_service import start_resize_stage
from app.services.format_service import start_format_stage
from app.services.watermark_service import start_watermark_stage
from app.database import init_db, SessionLocal, Proceso
import os

app = FastAPI()
process_store = {}

# Inicializa la DB al arrancar
init_db()

@app.get("/")
def root():
    return {"message": "PMIC Backend funcionando correctamente"}


def run_full_process(request: ProcessRequest, process_id: str):
    db = SessionLocal()
    try:
        # 🔹 ETAPA 1: Descarga
        start_download_stage(
            urls=request.urls,
            num_workers=request.workers.descarga,
            process_id=process_id,
            process_store=process_store
        )

        downloaded_paths = [
            os.path.join("storage/downloads", d["filename"])
            for d in process_store[process_id]["downloads"]
            if "filename" in d  # ← solo las exitosas, ignora las fallidas
        ]

        # 🔹 ETAPA 2: Redimensionamiento
        start_resize_stage(
            image_paths=downloaded_paths,
            num_workers=request.workers.redimension,
            process_id=process_id,
            process_store=process_store
        )

        resized_paths = [
            os.path.join("storage/downloads", r["resized_image"])
            for r in process_store[process_id]["resizes"]
            if "resized_image" in r
        ]

        # 🔹 ETAPA 3: Conversión de Formato
        start_format_stage(
            image_paths=resized_paths,
            num_workers=request.workers.formato,
            process_id=process_id,
            process_store=process_store
        )

        formatted_paths = [
            os.path.join("storage/downloads", f["converted_image"])
            for f in process_store[process_id]["formats"]
            if "converted_image" in f
        ]

        # 🔹 ETAPA 4: Marca de Agua
        start_watermark_stage(
            image_paths=formatted_paths,
            num_workers=request.workers.marca_agua,
            process_id=process_id,
            process_store=process_store
        )

        process_store[process_id]["status"] = "COMPLETADO"

        #  Guarda el proceso en DB
        db.query(Proceso).filter(Proceso.process_id == process_id).update({
            "status": "COMPLETADO",
            "end_time": datetime.now()
        })
        db.commit()

    except Exception as e:
        process_store[process_id]["status"] = "FALLIDO"
        process_store[process_id]["error_message"] = str(e)
        db.query(Proceso).filter(Proceso.process_id == process_id).update({
            "status": "FALLIDO",
            "end_time": datetime.now()
        })
        db.commit()

    finally:
        process_store[process_id]["end_time"] = datetime.now()
        db.close()


@app.post("/process")
def start_process(request: ProcessRequest, background_tasks: BackgroundTasks):
    process_id = str(uuid4())

    process_store[process_id] = {
        "status": "EN_PROCESO",
        "start_time": datetime.now(),
        "end_time": None,
        "request_data": request.dict(),
        "downloads": [],
        "download_errors": 0,
        "resizes": [],
        "resize_errors": 0,
        "formats": [],
        "format_errors": 0,
        "watermarks": [],
        "watermark_errors": 0
    }

    #  Guarda el proceso en DB
    db = SessionLocal()
    nuevo_proceso = Proceso(
        process_id = process_id,
        status     = "EN_PROCESO",
        start_time = datetime.now(),
        urls       = ",".join(str(url) for url in request.urls)  #  convierte a str
    )
    db.add(nuevo_proceso)
    db.commit()
    db.close()

    background_tasks.add_task(run_full_process, request, process_id)

    return {
        "process_id": process_id,
        "message": "Procesamiento iniciado correctamente"
    }


def calcular_metricas_etapa(registros: list, campo_tiempo: str):
    exitosos = [r for r in registros if "error" not in r]
    fallidos  = [r for r in registros if "error" in r]
    tiempos   = [r[campo_tiempo] for r in exitosos if campo_tiempo in r]

    total_acumulado = round(sum(tiempos), 4)
    promedio        = round(total_acumulado / len(tiempos), 4) if tiempos else 0.0

    return {
        "total_procesados": len(exitosos),
        "total_fallidos":   len(fallidos),
        "tiempo_total_acumulado": total_acumulado,
        "tiempo_promedio":  promedio
    }


def determinar_status(data: dict) -> str:
    if data["status"] == "EN_PROCESO":
        return "EN_PROCESO"

    total_errores = (
        data.get("download_errors", 0) +
        data.get("resize_errors", 0) +
        data.get("format_errors", 0) +
        data.get("watermark_errors", 0)
    )

    if data["status"] == "ERROR":
        return "FALLIDO"
    if total_errores > 0:
        return "COMPLETADO_CON_ERRORES"
    return "COMPLETADO"


@app.get("/process/{process_id}")
def get_process(process_id: str):
    if process_id not in process_store:
        raise HTTPException(status_code=404, detail="Proceso no encontrado")

    data = process_store[process_id]

    # ── Tiempo total ──────────────────────────────────────────────
    start_time = data.get("start_time")
    end_time   = data.get("end_time")

    if start_time and end_time:
        tiempo_total = round((end_time - start_time).total_seconds(), 4)
    elif start_time:
        tiempo_total = round((datetime.now() - start_time).total_seconds(), 4)
    else:
        tiempo_total = None

    # ── Métricas por etapa ────────────────────────────────────────
    metricas_descarga   = calcular_metricas_etapa(data.get("downloads",  []), "download_time_seconds")
    metricas_resize     = calcular_metricas_etapa(data.get("resizes",    []), "resize_time_seconds")
    metricas_formato    = calcular_metricas_etapa(data.get("formats",    []), "format_time_seconds")
    metricas_marca_agua = calcular_metricas_etapa(data.get("watermarks", []), "watermark_time_seconds")

    # ── Resumen global ────────────────────────────────────────────
    total_recibidos = len(data.get("request_data", {}).get("urls", []))
    total_errores   = (
        metricas_descarga["total_fallidos"] +
        metricas_resize["total_fallidos"] +
        metricas_formato["total_fallidos"] +
        metricas_marca_agua["total_fallidos"]
    )
    total_exitosos      = total_recibidos - metricas_descarga["total_fallidos"]
    porcentaje_exito    = round((total_exitosos / total_recibidos) * 100, 2) if total_recibidos else 0.0
    porcentaje_fallo    = round(100 - porcentaje_exito, 2)

    return {
        "informacion_general": {
            "process_id":             process_id,
            "status":                 determinar_status(data),
            "start_time":             start_time.isoformat() if start_time else None,
            "end_time":               end_time.isoformat() if end_time else None,
            "tiempo_total_ejecucion": tiempo_total
        },
        "metricas_por_etapa": {
            "descarga":    metricas_descarga,
            "redimension": metricas_resize,
            "formato":     metricas_formato,
            "marca_agua":  metricas_marca_agua
        },
        "resumen_global": {
            "total_archivos_recibidos": total_recibidos,
            "total_archivos_con_error": total_errores,
            "porcentaje_exito":         porcentaje_exito,
            "porcentaje_fallo":         porcentaje_fallo
        }
    }