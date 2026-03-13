import os

from app.models.request_models import ProcessRequest
from app.services.pipeline.stages.download_stage import start_download_stage


def run_download_step(request: ProcessRequest, process_id: str, process_store: dict):
    start_download_stage(
        urls=request.urls,
        num_workers=request.workers.descarga,
        process_id=process_id,
        process_store=process_store,
    )

    return [
        os.path.join("storage/downloads", item["filename"])
        for item in process_store[process_id]["downloads"]
        if "filename" in item
    ]
