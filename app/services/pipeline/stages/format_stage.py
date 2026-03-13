from queue import Queue

from app.services.pipeline.workers.format_worker import FormatWorker


def start_format_stage(image_paths, num_workers, process_id, process_store):
    format_queue = Queue()

    for path in image_paths:
        format_queue.put(path)

    process_store[process_id]["formats"] = []
    process_store[process_id]["format_errors"] = 0

    workers = []

    for _ in range(num_workers):
        worker = FormatWorker(format_queue, process_id, process_store)
        worker.start()
        workers.append(worker)

    format_queue.join()

    for worker in workers:
        worker.join()
