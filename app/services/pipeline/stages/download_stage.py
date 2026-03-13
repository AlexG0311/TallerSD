import os
from queue import Queue

from app.services.pipeline.workers.download_worker import DownloadWorker


def start_download_stage(urls, num_workers, process_id, process_store):
    os.makedirs("storage/downloads", exist_ok=True)
    download_queue = Queue()

    for url in urls:
        download_queue.put(str(url))

    process_store[process_id]["downloads"] = []
    process_store[process_id]["download_errors"] = 0

    workers = []

    for _ in range(num_workers):
        worker = DownloadWorker(download_queue, process_id, process_store)
        worker.start()
        workers.append(worker)

    download_queue.join()

    for worker in workers:
        worker.join()
