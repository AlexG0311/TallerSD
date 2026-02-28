import os
import time
import threading
from queue import Queue
from datetime import datetime
from PIL import Image


NUEVO_ANCHO_DEFAULT = 800


class ResizeWorker(threading.Thread):

    def __init__(self, queue, process_id, process_store, nuevo_ancho):
        super().__init__()
        self.queue = queue
        self.process_id = process_id
        self.process_store = process_store
        self.nuevo_ancho = nuevo_ancho

    def run(self):
        while True:
            try:
                image_path = self.queue.get_nowait()
            except:
                break

            print(f"[{self.name}] Redimensionando: {image_path}")

            start_time = time.time()

            try:
                with Image.open(image_path) as img:

                    ancho_original, alto_original = img.size

                    # Fórmula para mantener proporción
                    nuevo_ancho = self.nuevo_ancho
                    nuevo_alto = int(alto_original * (nuevo_ancho / ancho_original))

                    resized_img = img.resize((nuevo_ancho, nuevo_alto))

                    base, ext = os.path.splitext(image_path)
                    new_filename = f"{base}_redimensionado{ext}"

                    resized_img.save(new_filename)

                end_time = time.time()

                metadata = {
                    "original_image": os.path.basename(image_path),
                    "resized_image": os.path.basename(new_filename),
                    "dimensiones_originales": f"{ancho_original}x{alto_original}",
                    "dimensiones_nuevas": f"{nuevo_ancho}x{nuevo_alto}",
                    "resize_time_seconds": round(end_time - start_time, 4),
                    "worker_name": self.name,
                    "timestamp": datetime.now().isoformat()
                }

                self.process_store[self.process_id]["resizes"].append(metadata)

                print(f"[{self.name}] Redimensión exitosa: {nuevo_ancho}x{nuevo_alto}")

            except Exception as e:
                print(f"[{self.name}] ERROR resize: {e}")
                self.process_store[self.process_id]["resize_errors"] += 1

            finally:
                self.queue.task_done()


def start_resize_stage(image_paths, num_workers, process_id, process_store, nuevo_ancho=NUEVO_ANCHO_DEFAULT):

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