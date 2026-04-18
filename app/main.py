"""FastAPI application for SMS spam detection."""

import os
import sys

import joblib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import HealthResponse, PredictRequest, PredictResponse

LABEL_MAP = {0: "normal", 1: "spam", 2: "promo"}

MODEL_PATH = os.environ.get(
    "MODEL_PATH",
    os.path.join(os.path.dirname(__file__), "..", "training", "artifacts", "model.pkl"),
)

app = FastAPI(title="SMS Spam Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_model = None


def _get_model():
    """Lazy-load the ML model from disk."""
    global _model
    if _model is None:
        resolved = os.path.abspath(MODEL_PATH)
        if not os.path.exists(resolved):
            raise RuntimeError(f"Model not found at {resolved}")
        _model = joblib.load(resolved)
        print(f"Model loaded from: {resolved}")
    return _model


@app.on_event("startup")
def startup_event():
    """Load model on startup — fail fast if missing."""
    try:
        _get_model()
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


@app.get("/health", response_model=HealthResponse)
def health():
    """Health check endpoint."""
    return HealthResponse(status="healthy")


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    """Predict spam/not spam for the given text."""
    model = _get_model()
    prediction = int(model.predict([request.text])[0])
    label = LABEL_MAP.get(prediction, "unknown")
    return PredictResponse(prediction=prediction, label=label)
