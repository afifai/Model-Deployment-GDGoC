"""Tests for the FastAPI SMS spam detection API."""

import os

from fastapi.testclient import TestClient

# Ensure MODEL_PATH points to the trained model
os.environ.setdefault(
    "MODEL_PATH",
    os.path.join(os.path.dirname(__file__), "..", "training", "artifacts", "model.pkl"),
)

from app.main import app  # noqa: E402

client = TestClient(app)


def test_health_returns_healthy():
    """Test GET /health returns status healthy."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_predict_valid_text():
    """Test POST /predict with valid text returns valid response."""
    response = client.post("/predict", json={"text": "Halo apa kabar?"})
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "label" in data
    assert data["prediction"] in (0, 1, 2)
    label_map = {0: "normal", 1: "spam", 2: "promo"}
    assert data["label"] == label_map[data["prediction"]]


def test_predict_empty_text_returns_422():
    """Test POST /predict with empty text returns HTTP 422."""
    response = client.post("/predict", json={"text": ""})
    assert response.status_code == 422


def test_predict_whitespace_only_returns_422():
    """Test POST /predict with whitespace-only text returns HTTP 422."""
    response = client.post("/predict", json={"text": "   "})
    assert response.status_code == 422


def test_predict_missing_text_returns_422():
    """Test POST /predict with missing text field returns HTTP 422."""
    response = client.post("/predict", json={})
    assert response.status_code == 422
