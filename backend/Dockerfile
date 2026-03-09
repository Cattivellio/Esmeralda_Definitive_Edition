FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar algunas librerías si fuera necesario
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requerimientos e instalar
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . .

# Exponer el puerto de FastAPI
EXPOSE 8000

# Comando para iniciar la aplicación
# Usamos workers=1 porque con SQLite en RPi es más estable para evitar bloqueos de DB
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
