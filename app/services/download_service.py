import os
import time
import threading
import requests
from queue import Queue
from datetime import datetime


class DownloadWorker(threading.Thread):

    def __init__(self, queue, process_id, process_store):
        super().__init__()
        self.queue = queue
        self.process_id = process_id
        self.process_store = process_store

    def run(self):   # 👈 AHORA SÍ dentro de la clase
        while True:
            try:
                url = self.queue.get_nowait()
            except:
                break

            print(f"[{self.name}] Descargando: {url}")

            start_time = time.time()

            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()

                filename = f"{self.name}_{int(time.time())}.jpg"
                filepath = os.path.join("storage/downloads", filename)

                with open(filepath, "wb") as f:
                    f.write(response.content)

                end_time = time.time()

                file_size_mb = round(os.path.getsize(filepath) / (1024 * 1024), 4)

                metadata = {
                    "filename": filename,
                    "download_time_seconds": round(end_time - start_time, 4),
                    "file_size_mb": file_size_mb,
                    "worker_name": self.name,
                    "timestamp": datetime.now()
                }

                self.process_store[self.process_id]["downloads"].append(metadata)

                print(f"[{self.name}] Descarga exitosa")

            except Exception as e:
                print(f"[{self.name}] ERROR: {e}")
                self.process_store[self.process_id]["download_errors"] += 1

            finally:
                self.queue.task_done()


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

    return