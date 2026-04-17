FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all source code
COPY app/ ./app/
COPY training/ ./training/
COPY scripts/ ./scripts/

# Train model inside the container build
RUN python training/train.py

ENV MODEL_PATH=/app/training/artifacts/model.pkl

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
