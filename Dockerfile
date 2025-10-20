# Dockerfile para FastAPI + SQLAlchemy
# Usamos Python 3.11 para alinear con CI y evitar incompatibilidades
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependencias del sistema mínimas (psycopg ya viene como wheel, pero add-apt para contingencias)
RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
	libpq-dev \
	&& rm -rf /var/lib/apt/lists/*

# Copiamos solo archivos de dependencias primero para aprovechar cache
COPY requirements.txt constraints.txt ./
RUN pip install --no-cache-dir -r requirements.txt -c constraints.txt

# Copia del resto del código
COPY . .

EXPOSE 8000

# Ejecuta con uvicorn enlazando a 0.0.0.0 (para contenedor)
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
