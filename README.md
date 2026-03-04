# 1. Eliminar el venv actual (si existe)
rmdir /s /q venv

# 2. Crear nuevo venv
python -m venv venv

# 3. Activarlo
venv\Scripts\activate

# 4. Instalar dependencias
pip install -r requirements.txt


# 4. Instalar SqlLite
pip install sqlalchemy
