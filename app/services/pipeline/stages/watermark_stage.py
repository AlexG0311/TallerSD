from queue import Queue

from app.services.pipeline.workers.watermark_worker import WatermarkWorker


def start_watermark_stage(image_paths, num_workers, process_id, process_store):
    watermark_queue = Queue()

    for path in image_paths:
        watermark_queue.put(path)

    process_store[process_id]["watermarks"] = []
    process_store[process_id]["watermark_errors"] = 0

    workers = []

    for _ in range(num_workers):
        worker = WatermarkWorker(watermark_queue, process_id, process_store)
        worker.start()
        workers.append(worker)

    watermark_queue.join()

    for worker in workers:
        worker.join()
