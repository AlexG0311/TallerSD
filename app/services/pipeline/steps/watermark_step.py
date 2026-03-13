from app.models.request_models import ProcessRequest
from app.services.pipeline.stages.watermark_stage import start_watermark_stage


def run_watermark_step(
    request: ProcessRequest,
    process_id: str,
    process_store: dict,
    image_paths,
):
    start_watermark_stage(
        image_paths=image_paths,
        num_workers=request.workers.marca_agua,
        process_id=process_id,
        process_store=process_store,
    )
