FROM python:3.11-slim

WORKDIR /app

# Kopiowanie plików
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ekspozycja portu FastAPI
EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]