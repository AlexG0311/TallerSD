import os
import time
import threading
from queue import Queue
from datetime import datetime
from PIL import Image


class FormatWorker(threading.Thread):

    def __init__(self, queue, process_id, process_store):
        super().__init__()
        self.queue = queue
        self.process_id = process_id
        self.process_store = process_store

    def run(self):
        while True:
            try:
                image_path = self.queue.get_nowait()
            except:
                break

            print(f"[{self.name}] Convirtiendo formato: {image_path}")

            start_time = time.time()

            try:
                with Image.open(image_path) as img:

                    formato_original = img.format if img.format else "UNKNOWN"

                    # Si ya es PNG no hace falta convertir
                    if formato_original == "PNG":
                        print(f"[{self.name}] Ya es PNG, se omite: {image_path}")
                        end_time = time.time()
                        self.process_store[self.process_id]["formats"].append({
                            "original_image": os.path.basename(image_path),
                            "converted_image": os.path.basename(image_path),
                            "formato_original": formato_original,
                            "formato_nuevo": "PNG",
                            "conversion_realizada": False,
                            "format_time_seconds": round(end_time - start_time, 4),
                            "worker_name": self.name,
                            "timestamp": datetime.now().isoformat()
                        })
                        continue

                    # Convertir a PNG
                    base = os.path.splitext(image_path)[0]
                    new_filename = f"{base}_formato_cambiado.png"

                    # Convertir a RGB si tiene canal alpha (RGBA) para evitar errores
                    if img.mode in ("RGBA", "P"):
                        img = img.convert("RGBA")
                    else:
                        img = img.convert("RGB")

                    img.save(new_filename, format="PNG")

                end_time = time.time()

                metadata = {
                    "original_image": os.path.basename(image_path),
                    "converted_image": os.path.basename(new_filename),
                    "formato_original": formato_original,
                    "formato_nuevo": "PNG",
                    "conversion_realizada": True,
                    "format_time_seconds": round(end_time - start_time, 4),
                    "worker_name": self.name,
                    "timestamp": datetime.now().isoformat()
                }

                self.process_store[self.process_id]["formats"].append(metadata)

                print(f"[{self.name}] Conversión exitosa: {os.path.basename(new_filename)}")

            except Exception as e:
                print(f"[{self.name}] ERROR formato: {e}")
                self.process_store[self.process_id]["format_errors"] += 1

            finally:
                self.queue.task_done()


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
