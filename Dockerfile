FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY training/artifacts/model.pkl ./training/artifacts/model.pkl

ENV MODEL_PATH=/app/training/artifacts/model.pkl

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
