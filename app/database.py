from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///./pmic.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# ─── TABLAS ───────────────────────────────────────────

class Proceso(Base):
    __tablename__ = "procesos"

    process_id  = Column(String, primary_key=True)
    status      = Column(String)
    start_time  = Column(DateTime, default=datetime.now)
    end_time    = Column(DateTime, nullable=True)
    urls        = Column(Text)  # guardamos como string separado por comas


class Descarga(Base):
    __tablename__ = "descargas"

    id                    = Column(Integer, primary_key=True, autoincrement=True)
    process_id            = Column(String)
    filename              = Column(String)
    url                   = Column(String)
    file_size_mb          = Column(Float)
    download_time_seconds = Column(Float)
    worker_name           = Column(String)
    timestamp             = Column(DateTime, default=datetime.now)
    error                 = Column(String, nullable=True)


class Resize(Base):
    __tablename__ = "resizes"

    id                  = Column(Integer, primary_key=True, autoincrement=True)
    process_id          = Column(String)
    original_image      = Column(String)
    resized_image       = Column(String)
    resize_time_seconds = Column(Float)
    worker_name         = Column(String)
    timestamp           = Column(DateTime, default=datetime.now)
    error               = Column(String, nullable=True)


class Formato(Base):
    __tablename__ = "formatos"

    id                  = Column(Integer, primary_key=True, autoincrement=True)
    process_id          = Column(String)
    original_image      = Column(String)
    converted_image     = Column(String)
    formato_original    = Column(String)
    formato_nuevo       = Column(String)
    format_time_seconds = Column(Float)
    worker_name         = Column(String)
    timestamp           = Column(DateTime, default=datetime.now)
    error               = Column(String, nullable=True)


class MarcaAgua(Base):
    __tablename__ = "marcas_agua"

    id                      = Column(Integer, primary_key=True, autoincrement=True)
    process_id              = Column(String)
    original_image          = Column(String)
    watermarked_image       = Column(String)
    watermark_time_seconds  = Column(Float)
    worker_name             = Column(String)
    timestamp               = Column(DateTime, default=datetime.now)
    error                   = Column(String, nullable=True)


def init_db():
    Base.metadata.create_all(bind=engine)