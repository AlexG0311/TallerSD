import os
import time
import threading

import requests
from datetime import datetime

from app.database import SessionLocal, Descarga


class DownloadWorker(threading.Thread):

    def __init__(self, queue, process_id, process_store):
        super().__init__()
        self.queue = queue
        self.process_id = process_id
        self.process_store = process_store

    def run(self):
        while True:
            try:
                url = self.queue.get_nowait()
            except:
                break

            start_time = time.time()
            db = SessionLocal()

            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()

                filename = f"{self.name}_{int(time.time())}.jpg"
                filepath = os.path.join("storage/downloads", filename)
                with open(filepath, "wb") as f:
                    f.write(response.content)

                elapsed = round(time.time() - start_time, 4)
                file_size_mb = round(os.path.getsize(filepath) / (1024 * 1024), 4)

                metadata = {
                    "filename": filename,
                    "url": url,
                    "file_size_mb": file_size_mb,
                    "download_time_seconds": elapsed,
                    "worker_name": self.name,
                    "timestamp": datetime.now().isoformat(),
                }

                self.process_store[self.process_id]["downloads"].append(metadata)

                db.add(
                    Descarga(
                        process_id=self.process_id,
                        filename=filename,
                        url=url,
                        file_size_mb=file_size_mb,
                        download_time_seconds=elapsed,
                        worker_name=self.name,
                        timestamp=datetime.now(),
                    )
                )
                db.commit()

            except Exception as e:
                self.process_store[self.process_id]["download_errors"] += 1
                self.process_store[self.process_id]["downloads"].append(
                    {
                        "url": url,
                        "error": str(e),
                        "worker_name": self.name,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

                db.add(
                    Descarga(
                        process_id=self.process_id,
                        url=url,
                        worker_name=self.name,
                        error=str(e),
                        timestamp=datetime.now(),
                    )
                )
                db.commit()

            finally:
                db.close()
                self.queue.task_done()
