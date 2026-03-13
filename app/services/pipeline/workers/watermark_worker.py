import os
import time
import threading

from datetime import datetime
from queue import Empty
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
            except Empty:
                break

            print(f"[{self.name}] Aplicando marca de agua: {image_path}")
            start_time = time.time()

            try:
                with Image.open(image_path).convert("RGBA") as img:
                    watermark_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
                    draw = ImageDraw.Draw(watermark_layer)

                    texto = "PMIC 2026"

                    try:
                        font = ImageFont.truetype("arial.ttf", size=40)
                    except:
                        font = ImageFont.load_default()

                    bbox = draw.textbbox((0, 0), texto, font=font)
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    x = img.width - text_width - 20
                    y = img.height - text_height - 20

                    draw.text((x, y), texto, font=font, fill=(255, 255, 255, 128))

                    combined = Image.alpha_composite(img, watermark_layer)
                    final_img = combined.convert("RGB")

                    base = os.path.splitext(os.path.basename(image_path))[0]
                    output_dir = os.path.dirname(image_path)
                    new_filename = os.path.join(output_dir, f"{base}_marca_agua.png")
                    final_img.save(new_filename, format="PNG")

                elapsed = round(time.time() - start_time, 4)

                metadata = {
                    "original_image": os.path.basename(image_path),
                    "watermarked_image": os.path.basename(new_filename),
                    "texto_marca_agua": texto,
                    "watermark_time_seconds": elapsed,
                    "worker_name": self.name,
                    "timestamp": datetime.now().isoformat(),
                }

                self.process_store[self.process_id]["watermarks"].append(metadata)

                db = SessionLocal()
                db.add(
                    MarcaAgua(
                        process_id=self.process_id,
                        original_image=metadata["original_image"],
                        watermarked_image=metadata["watermarked_image"],
                        watermark_time_seconds=metadata["watermark_time_seconds"],
                        worker_name=self.name,
                        timestamp=datetime.now(),
                    )
                )
                db.commit()
                db.close()
                print(f"[{self.name}] Marca de agua aplicada: {new_filename}")

            except Exception as e:
                print(f"[{self.name}] ERROR watermark: {e}")
                self.process_store[self.process_id]["watermark_errors"] += 1
                self.process_store[self.process_id]["watermarks"].append(
                    {
                        "original_image": os.path.basename(image_path),
                        "error": str(e),
                        "worker_name": self.name,
                        "timestamp": datetime.now().isoformat(),
                    }
                )
                db = SessionLocal()
                db.add(
                    MarcaAgua(
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