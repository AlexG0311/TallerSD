from fastapi import FastAPI, HTTPException, BackgroundTasks
from uuid import uuid4
from datetime import datetime
from app.models.request_models import ProcessRequest
from app.services.download_service import start_download_stage
from app.services.resize_service import start_resize_stage
from app.services.format_service import start_format_stage
import os

app = FastAPI()

process_store = {}


@app.get("/")
def root():
    return {"message": "PMIC Backend funcionando correctamente"}


# 🔹 FUNCIÓN QUE CORRE EN SEGUNDO PLANO
def run_full_process(request: ProcessRequest, process_id: str):

    try:
        start_download_stage(
            urls=request.urls,
            num_workers=request.workers.descarga,
            process_id=process_id,
            process_store=process_store
        )

        # Obtener rutas de archivos descargados
        downloaded_paths = [
            os.path.join("storage/downloads", d["filename"])
            for d in process_store[process_id]["downloads"]
        ]

        start_resize_stage(
            image_paths=downloaded_paths,
            num_workers=request.workers.redimension,
            process_id=process_id,
            process_store=process_store
        )

        # Obtener rutas de imágenes redimensionadas
        resized_paths = [
            os.path.join("storage/downloads", r["resized_image"])
            for r in process_store[process_id]["resizes"]
            if "resized_image" in r
        ]

        start_format_stage(
            image_paths=resized_paths,
            num_workers=request.workers.formato,
            process_id=process_id,
            process_store=process_store
        )

        process_store[process_id]["status"] = "COMPLETADO"

    except Exception as e:
        process_store[process_id]["status"] = "ERROR"
        process_store[process_id]["error_message"] = str(e)

    finally:
        process_store[process_id]["end_time"] = datetime.now()


# 🔹 ENDPOINT POST (AHORA NO BLOQUEA)
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
        "format_errors": 0
    }

    # Aquí lanzamos el proceso en background
    background_tasks.add_task(
        run_full_process,
        request,
        process_id
    )

    return {
        "process_id": process_id,
        "message": "Procesamiento iniciado correctamente"
    }


@app.get("/process/{process_id}")
def get_process(process_id: str):
    if process_id not in process_store:
        raise HTTPException(status_code=404, detail="Proceso no encontrado")

    return {
        "process_id": process_id,
        **process_store[process_id]
    }