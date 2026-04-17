"""FastAPI application for SMS spam detection."""

import os
import sys

import joblib
from fastapi import FastAPI

from app.schemas import HealthResponse, PredictRequest, PredictResponse

LABEL_MAP = {0: "normal", 1: "unknown", 2: "spam"}

MODEL_PATH = os.environ.get(
    "MODEL_PATH",
    os.path.join(os.path.dirname(__file__), "..", "training", "artifacts", "model.pkl"),
)


def _load_model():
    """Load the ML model from disk."""
    resolved = os.path.abspath(MODEL_PATH)
    if not os.path.exists(resolved):
        print(f"Error: Model not found at {resolved}", file=sys.stderr)
        sys.exit(1)
    loaded = joblib.load(resolved)
    print(f"Model loaded from: {resolved}")
    return loaded


model = _load_model()

app = FastAPI(title="SMS Spam Detection API")


@app.get("/health", response_model=HealthResponse)
def health():
    """Health check endpoint."""
    return HealthResponse(status="healthy")


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    """Predict spam/not spam for the given text."""
    prediction = int(model.predict([request.text])[0])
    label = LABEL_MAP.get(prediction, "unknown")
    return PredictResponse(prediction=prediction, label=label)
