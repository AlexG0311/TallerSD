from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.database import Proceso, SessionLocal
from app.models.request_models import ProcessRequest
from app.services.pipeline.process_orchestrator import run_full_process
from app.services.reporting.process_summary_service import build_process_response
from app.state import process_store

router = APIRouter()


@router.get("/")
def root():
    return {"message": "PMIC Backend funcionando correctamente"}


@router.post("/process")
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
        "watermark_errors": 0,
    }

    db = SessionLocal()
    nuevo_proceso = Proceso(
        process_id=process_id,
        status="EN_PROCESO",
        start_time=datetime.now(),
        urls=",".join(str(url) for url in request.urls),
    )
    db.add(nuevo_proceso)
    db.commit()
    db.close()

    background_tasks.add_task(run_full_process, request, process_id, process_store)

    return {
        "process_id": process_id,
        "message": "Procesamiento iniciado correctamente",
    }


@router.get("/process/{process_id}")
def get_process(process_id: str):
    if process_id not in process_store:
        raise HTTPException(status_code=404, detail="Proceso no encontrado")

    data = process_store[process_id]

    return build_process_response(process_id, data)
