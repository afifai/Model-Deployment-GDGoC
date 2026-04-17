"""Pydantic schemas for the SMS spam detection API."""

from pydantic import BaseModel, field_validator


class PredictRequest(BaseModel):
    """Request schema for the /predict endpoint."""

    text: str

    @field_validator("text")
    @classmethod
    def text_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("text must not be empty or whitespace-only")
        return v


class PredictResponse(BaseModel):
    """Response schema for the /predict endpoint."""

    prediction: int
    label: str


class HealthResponse(BaseModel):
    """Response schema for the /health endpoint."""

    status: str
