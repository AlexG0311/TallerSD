import os
import time
import threading

from datetime import datetime
from PIL import Image

from app.database import SessionLocal, Resize


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
                    "timestamp": datetime.now().isoformat(),
                }

                self.process_store[self.process_id]["resizes"].append(metadata)

                db = SessionLocal()
                db.add(
                    Resize(
                        process_id=self.process_id,
                        original_image=metadata["original_image"],
                        resized_image=metadata["resized_image"],
                        resize_time_seconds=metadata["resize_time_seconds"],
                        worker_name=self.name,
                        timestamp=datetime.now(),
                    )
                )
                db.commit()
                db.close()

                print(f"[{self.name}] Redimensión exitosa: {nuevo_ancho}x{nuevo_alto}")

            except Exception as e:
                print(f"[{self.name}] ERROR resize: {e}")
                self.process_store[self.process_id]["resize_errors"] += 1
                self.process_store[self.process_id]["resizes"].append(
                    {
                        "original_image": os.path.basename(image_path),
                        "error": str(e),
                        "worker_name": self.name,
                        "timestamp": datetime.now().isoformat(),
                    }
                )
                db = SessionLocal()
                db.add(
                    Resize(
                        process_id=self.process_id,
                        original_image=os.path.basename(image_path),
                        worker_name=self.name,
                        error=str(e),
                        timestamp=datetime.now(),
                    )
                )
                db.commit()
                db.close()

            finally:
                self.queue.task_done()
