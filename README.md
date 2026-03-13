# 1. Eliminar el venv actual (si existe)
rmdir /s /q venv

# 2. Crear nuevo venv
python -m venv venv

# 3. Activarlo
venv\Scripts\activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5 Levantar el entorno
uvicorn app.main:app --reload

# Instalar SqlLite 
pip install sqlalchemy

# Actualizar requirements.txt cuando se agreguen otras depe
pip freeze > requirements.txt

## Diagramas

![Arquitectura del sistema](doc/diagramas/arquitectura_sistema.jpeg)
![Arquitectura de software](doc/diagramas/arquitectura_software.png)


