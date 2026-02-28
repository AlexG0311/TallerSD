from pydantic import BaseModel, HttpUrl
from typing import List


class WorkersConfig(BaseModel):
    descarga: int
    redimension: int
    formato: int
    marca_agua: int


class ProcessRequest(BaseModel):
    urls: List[HttpUrl]
    workers: WorkersConfig