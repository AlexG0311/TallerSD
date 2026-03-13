import os

from app.models.request_models import ProcessRequest
from app.services.pipeline.stages.format_stage import start_format_stage


def run_format_step(
    request: ProcessRequest,
    process_id: str,
    process_store: dict,
    image_paths,
):
    start_format_stage(
        image_paths=image_paths,
        num_workers=request.workers.formato,
        process_id=process_id,
        process_store=process_store,
    )

    return [
        os.path.join("storage/downloads", item["converted_image"])
        for item in process_store[process_id]["formats"]
        if "converted_image" in item
    ]
