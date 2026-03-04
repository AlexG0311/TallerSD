import threading
import os
import time
from queue import Queue
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from app.database import SessionLocal, MarcaAgua


class WatermarkWorker(threading.Thread):

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

            print(f"[{self.name}] Aplicando marca de agua: {image_path}")
            start_time = time.time()

            try:
                with Image.open(image_path).convert("RGBA") as img:

                    # Crear capa transparente para la marca de agua
                    watermark_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
                    draw = ImageDraw.Draw(watermark_layer)

                    texto = "PMIC 2026"

                    # Intentar usar fuente, si no usar default
                    try:
                        font = ImageFont.truetype("arial.ttf", size=40)
                    except:
                        font = ImageFont.load_default()

                    # Calcular posición (esquina inferior derecha)
                    bbox = draw.textbbox((0, 0), texto, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    x = img.width - text_width - 20
                    y = img.height - text_height - 20

                    # Dibujar texto con transparencia
                    draw.text((x, y), texto, font=font, fill=(255, 255, 255, 128))

                    # Combinar imagen origina l con marca de agua
                    combined = Image.alpha_composite(img, watermark_layer)
                    final_img = combined.convert("RGB")

                    # Guardar con   sufijo _marca_agua
                    base = os.path.splitext(os.path.basename(image_path))[0]
                    output_dir = os.path.dirname(image_path)
                    new_filename = os.path.join(output_dir, f"{base}_marca_agua.png")
                    final_img.save(new_filename, format="PNG")

                end_time = time.time()

                metadata = {
                    "original_image": os.path.basename(image_path),
                    "watermarked_image": os.path.basename(new_filename),
                    "texto_marca_agua": texto,
                    "watermark_time_seconds": round(end_time - start_time, 4),
                    "worker_name": self.name,
                    "timestamp": datetime.now().isoformat()
                }

                self.process_store[self.process_id]["watermarks"].append(metadata)

                #  Guardar en DB
                db = SessionLocal()
                db.add(MarcaAgua(
                    process_id             = self.process_id,
                    original_image         = metadata["original_image"],
                    watermarked_image      = metadata["watermarked_image"],
                    watermark_time_seconds = metadata["watermark_time_seconds"],
                    worker_name            = self.name,
                    timestamp              = datetime.now()
                ))
                db.commit()
                db.close()
                print(f"[{self.name}]  Marca de agua aplicada: {new_filename}")

            except Exception as e:
                self.process_store[self.process_id]["watermark_errors"] += 1
                self.process_store[self.process_id]["watermarks"].append({
                    "original_image": os.path.basename(image_path),
                    "error": str(e),
                    "worker_name": self.name,
                    "timestamp": datetime.now().isoformat()
                })
                db = SessionLocal()
                db.add(MarcaAgua(
                    process_id     = self.process_id,
                    original_image = os.path.basename(image_path),
                    worker_name    = self.name,
                    error          = str(e),
                    timestamp      = datetime.now()
                ))
                db.commit()
                db.close()
                print(f"[{self.name}]  Error: {e}")

            finally:
                self.queue.task_done()


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