FROM python:3.11-slim

WORKDIR /app

# Instalacja zależności systemowych
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Kopiowanie plików
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Sprawdzenie czy model istnieje
RUN test -f model.joblib || echo "WARNING: model.joblib not found!"

CMD ["python", "-u", "app.py"]