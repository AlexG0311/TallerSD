from queue import Queue

from app.services.pipeline.workers.resize_worker import NUEVO_ANCHO_DEFAULT, ResizeWorker


def start_resize_stage(
    image_paths,
    num_workers,
    process_id,
    process_store,
    nuevo_ancho=NUEVO_ANCHO_DEFAULT,
):
    resize_queue = Queue()

    for path in image_paths:
        resize_queue.put(path)

    process_store[process_id]["resizes"] = []
    process_store[process_id]["resize_errors"] = 0

    workers = []

    for _ in range(num_workers):
        worker = ResizeWorker(resize_queue, process_id, process_store, nuevo_ancho)
        worker.start()
        workers.append(worker)

    resize_queue.join()

    for worker in workers:
        worker.join()
