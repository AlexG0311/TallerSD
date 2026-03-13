import os
import time
import threading

from datetime import datetime
from queue import Empty
from PIL import Image

from app.database import SessionLocal, Formato


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
            except Empty:
                break

            print(f"[{self.name}] Convirtiendo formato: {image_path}")
            start_time = time.time()

            try:
                with Image.open(image_path) as img:
                    formato_original = img.format if img.format else "UNKNOWN"

                    if formato_original == "PNG":
                        print(f"[{self.name}] Ya es PNG, se omite: {image_path}")
                        elapsed = round(time.time() - start_time, 4)
                        self.process_store[self.process_id]["formats"].append(
                            {
                                "original_image": os.path.basename(image_path),
                                "converted_image": os.path.basename(image_path),
                                "formato_original": formato_original,
                                "formato_nuevo": "PNG",
                                "conversion_realizada": False,
                                "format_time_seconds": elapsed,
                                "worker_name": self.name,
                                "timestamp": datetime.now().isoformat(),
                            }
                        )
                    else:
                        base = os.path.splitext(image_path)[0]
                        new_filename = f"{base}_formato_cambiado.png"

                        if img.mode in ("RGBA", "P"):
                            img = img.convert("RGBA")
                        else:
                            img = img.convert("RGB")

                        img.save(new_filename, format="PNG")
                        elapsed = round(time.time() - start_time, 4)

                        metadata = {
                            "original_image": os.path.basename(image_path),
                            "converted_image": os.path.basename(new_filename),
                            "formato_original": formato_original,
                            "formato_nuevo": "PNG",
                            "conversion_realizada": True,
                            "format_time_seconds": elapsed,
                            "worker_name": self.name,
                            "timestamp": datetime.now().isoformat(),
                        }

                        self.process_store[self.process_id]["formats"].append(metadata)

                        db = SessionLocal()
                        db.add(
                            Formato(
                                process_id=self.process_id,
                                original_image=metadata["original_image"],
                                converted_image=metadata["converted_image"],
                                formato_original=metadata["formato_original"],
                                formato_nuevo=metadata["formato_nuevo"],
                                format_time_seconds=metadata["format_time_seconds"],
                                worker_name=self.name,
                                timestamp=datetime.now(),
                            )
                        )
                        db.commit()
                        db.close()
                        print(f"[{self.name}] Conversión exitosa: {os.path.basename(new_filename)}")

            except Exception as e:
                print(f"[{self.name}] ERROR formato: {e}")
                self.process_store[self.process_id]["format_errors"] += 1
                self.process_store[self.process_id]["formats"].append(
                    {
                        "original_image": os.path.basename(image_path),
                        "error": str(e),
                        "worker_name": self.name,
                        "timestamp": datetime.now().isoformat(),
                    }
                )
                db = SessionLocal()
                db.add(
                    Formato(
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