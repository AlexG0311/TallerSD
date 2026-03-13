import os

from app.models.request_models import ProcessRequest
from app.services.pipeline.stages.resize_stage import start_resize_stage


def run_resize_step(
    request: ProcessRequest,
    process_id: str,
    process_store: dict,
    image_paths,
):
    start_resize_stage(
        image_paths=image_paths,
        num_workers=request.workers.redimension,
        process_id=process_id,
        process_store=process_store,
    )

    return [
        os.path.join("storage/downloads", item["resized_image"])
        for item in process_store[process_id]["resizes"]
        if "resized_image" in item
    ]
