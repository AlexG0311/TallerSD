from datetime import datetime

from app.database import Proceso, SessionLocal
from app.models.request_models import ProcessRequest
from app.services.pipeline.steps.download_step import run_download_step
from app.services.pipeline.steps.format_step import run_format_step
from app.services.pipeline.steps.resize_step import run_resize_step
from app.services.pipeline.steps.watermark_step import run_watermark_step


def run_full_process(request: ProcessRequest, process_id: str, process_store: dict):
    db = SessionLocal()
    try:
        downloaded_paths = run_download_step(request, process_id, process_store)
        resized_paths = run_resize_step(request, process_id, process_store, downloaded_paths)
        formatted_paths = run_format_step(request, process_id, process_store, resized_paths)
        run_watermark_step(request, process_id, process_store, formatted_paths)

        process_store[process_id]["status"] = "COMPLETADO"

        db.query(Proceso).filter(Proceso.process_id == process_id).update(
            {
                "status": "COMPLETADO",
                "end_time": datetime.now(),
            }
        )
        db.commit()

    except Exception as e:
        process_store[process_id]["status"] = "FALLIDO"
        process_store[process_id]["error_message"] = str(e)
        db.query(Proceso).filter(Proceso.process_id == process_id).update(
            {
                "status": "FALLIDO",
                "end_time": datetime.now(),
            }
        )
        db.commit()

    finally:
        process_store[process_id]["end_time"] = datetime.now()
        db.close()
