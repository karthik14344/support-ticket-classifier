"""API route definitions."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_app_settings, get_classifier_service
from app.config import Settings
from app.schemas.request_response import (
    APIInfoResponse,
    ClassifyRequest,
    ClassifyResponse,
    HealthResponse,
)
from app.services.classifier_service import ClassifierService
from app.utils.exceptions import AppError, LLMResponseError, LLMServiceError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=APIInfoResponse, tags=["Info"])
async def root(settings: Settings = Depends(get_app_settings)) -> APIInfoResponse:
    """Return API metadata and available endpoints."""
    return APIInfoResponse(
        name=settings.app_name,
        version=settings.app_version,
        description=settings.app_description,
        endpoints={
            "classify": "POST /classify",
            "health": "GET /health",
            "docs": "GET /docs",
        },
    )


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """Health check endpoint for monitoring and load balancers."""
    return HealthResponse(status="healthy")


@router.post(
    "/classify",
    response_model=ClassifyResponse,
    status_code=status.HTTP_200_OK,
    tags=["Classification"],
    summary="Classify a support ticket",
    description="Classify a customer support ticket into one of six categories using an LLM.",
)
async def classify_ticket(
    request: ClassifyRequest,
    classifier: ClassifierService = Depends(get_classifier_service),
) -> ClassifyResponse:
    """Classify a support ticket and return category with confidence score."""
    try:
        return await classifier.classify(request.ticket)
    except LLMResponseError as exc:
        logger.error("LLM response error: %s", exc.message)
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.message,
        ) from exc
    except LLMServiceError as exc:
        logger.error("LLM service error: %s", exc.message)
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.message,
        ) from exc
    except AppError as exc:
        logger.error("Application error: %s", exc.message)
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.message,
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error during classification.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during classification.",
        ) from exc
