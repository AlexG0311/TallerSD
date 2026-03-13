# 1. Eliminar el venv actual (si existe)
rmdir /s /q venv

# 2. Crear nuevo venv
python -m venv venv

# 3. Activarlo
venv\Scripts\activate

# 4. Instalar dependencias
pip install -r requirements.txt

# Instalar SqlLite
pip install sqlalchemy

# Actualizar requirements.txt cuando se agreguen otras depe
pip freeze > requirements.txt

# Levantar el entorno
uvicorn app.main:app --reload


![alt text](<arquitectura de software.png>) ![alt text](<arquitectura del sistema_.jpeg>)