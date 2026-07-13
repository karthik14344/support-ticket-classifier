"""Pydantic schemas for API request and response models."""

from pydantic import BaseModel, Field, field_validator


class ClassifyRequest(BaseModel):
    """Request body for ticket classification."""

    ticket: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Customer support ticket text to classify.",
        examples=["Payment was deducted twice."],
    )

    @field_validator("ticket")
    @classmethod
    def strip_ticket(cls, value: str) -> str:
        """Strip whitespace from ticket text."""
        stripped = value.strip()
        if not stripped:
            raise ValueError("Ticket text cannot be empty or whitespace only.")
        return stripped


class ClassifyResponse(BaseModel):
    """Response body for ticket classification."""

    ticket: str = Field(..., description="Original ticket text.")
    category: str = Field(..., description="Predicted category.")
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0 and 1.",
    )


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(default="healthy", description="Service health status.")


class APIInfoResponse(BaseModel):
    """Root endpoint API information."""

    name: str
    version: str
    description: str
    endpoints: dict[str, str]
