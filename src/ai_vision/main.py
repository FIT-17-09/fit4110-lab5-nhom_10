"""
AI Vision Service - FIT4110 A4
FastAPI service for image analysis using YOLO/mock AI.
"""

import os
import time
import random
from datetime import datetime, timezone
from typing import Dict, List, Optional
from collections import defaultdict
from enum import Enum

from fastapi import FastAPI, HTTPException, Header, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


SERVICE_NAME = os.getenv("SERVICE_NAME", "ai-vision")
SERVICE_VERSION = os.getenv("SERVICE_VERSION", "1.0.0")
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "a4-dev-token")
USE_MOCK_AI = os.getenv("USE_MOCK_AI", "true").lower() == "true"

app = FastAPI(
    title="AI Vision Service",
    version=SERVICE_VERSION,
    description="AI-powered image analysis service for Smart Campus Operations Platform",
)

# In-memory storage for stats
ANALYSIS_COUNT = 0
TOTAL_OBJECTS = 0
PROCESSING_TIMES = []
OBJECT_COUNTS = defaultdict(int)
RISK_COUNTS = defaultdict(int)

# Supported objects (YOLOv8 common classes)
SUPPORTED_OBJECTS = [
    "person", "bicycle", "car", "motorcycle", "bus", "truck",
    "dog", "cat", "backpack", "umbrella", "handbag", "suitcase"
]

# Risk level thresholds
RISK_THRESHOLDS = {
    "low": 3,
    "medium": 6,
    "high": 10,
    "critical": 15
}


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ImageAnalysisRequest(BaseModel):
    camera_id: str = Field(..., min_length=1, examples=["cam-gate-01"])
    image_url: Optional[str] = Field(default=None, examples=["http://example.com/frame.jpg"])
    image_data: Optional[str] = Field(default=None, description="Base64 encoded image")
    timestamp: str = Field(..., examples=["2026-05-02T09:10:00+07:00"])


class DetectedObject(BaseModel):
    object: str = Field(..., alias="object_name", examples=["person"])
    confidence: float = Field(..., ge=0, le=1, examples=[0.91])
    bbox: Optional[List[int]] = Field(default=None, examples=[[100, 50, 200, 300]])
    class_id: Optional[int] = None


class ImageAnalysisResponse(BaseModel):
    detected: bool
    objects: List[DetectedObject]
    risk_level: RiskLevel
    alert_triggered: bool = False
    processing_time_ms: int
    model_version: str = "yolov8n-mock"
    timestamp: str


class BatchImageItem(BaseModel):
    camera_id: str
    image_url: Optional[str] = None
    image_data: Optional[str] = None
    timestamp: str


class BatchAnalysisRequest(BaseModel):
    images: List[BatchImageItem] = Field(..., min_length=1, max_length=10)


class BatchAnalysisResponse(BaseModel):
    results: List[ImageAnalysisResponse]
    total_images: int
    processed: int
    failed: int
    processing_time_ms: int


class SupportedObjectsResponse(BaseModel):
    objects: List[str]
    model_name: str = "yolov8n"
    model_version: str = "8.0.0"
    detection_threshold: float = 0.5


class VisionStats(BaseModel):
    total_analyzed: int
    total_objects: int
    avg_processing_time_ms: float
    top_objects: List[Dict]
    risk_distribution: Dict[str, int]


class ProblemDetails(BaseModel):
    type: str = "about:blank"
    title: str
    status: int = Field(..., ge=400, le=599)
    detail: str
    instance: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


def build_problem(
    status_code: int,
    title: str,
    detail: str,
    instance: Optional[str] = None,
    problem_type: str = "about:blank",
) -> Dict:
    return {
        "type": problem_type,
        "title": title,
        "status": status_code,
        "detail": detail,
        "instance": instance,
    }


def calculate_risk_level(objects: List[DetectedObject]) -> tuple[RiskLevel, bool]:
    """Calculate risk level based on detected objects."""
    count = len(objects)
    
    if count == 0:
        return RiskLevel.LOW, False
    
    # Count object types
    obj_type_counts = defaultdict(int)
    for obj in objects:
        obj_type_counts[obj.object] += 1
    
    # Check for unknown persons
    person_count = obj_type_counts.get("person", 0)
    if person_count >= 10:
        return RiskLevel.CRITICAL, True
    elif person_count >= 5:
        return RiskLevel.HIGH, True
    elif count >= RISK_THRESHOLDS["high"]:
        return RiskLevel.HIGH, True
    elif count >= RISK_THRESHOLDS["medium"]:
        return RiskLevel.MEDIUM, False
    
    return RiskLevel.LOW, False


def mock_yolo_detection(camera_id: str) -> List[DetectedObject]:
    """
    Mock YOLO detection for testing without actual AI model.
    In production, replace with actual YOLO inference.
    """
    # Simulate different scenarios based on camera_id
    scenarios = {
        "cam-gate": [("person", 0.9), ("bicycle", 0.75)],
        "cam-parking": [("car", 0.88), ("person", 0.82)],
        "cam-main": [("person", 0.95)],
        "cam-entrance": [("person", 0.85), ("backpack", 0.65)],
    }
    
    objects = []
    
    # Find matching scenario
    matched = False
    for key, detections in scenarios.items():
        if key in camera_id.lower():
            for obj_name, conf in detections:
                objects.append(DetectedObject(
                    object=obj_name,
                    confidence=conf,
                    bbox=[
                        random.randint(50, 150),
                        random.randint(50, 150),
                        random.randint(100, 200),
                        random.randint(150, 300)
                    ]
                ))
            matched = True
            break
    
    # Default random detection if no scenario matched
    if not matched:
        if random.random() > 0.3:  # 70% chance of detection
            num_objects = random.randint(1, 3)
            for _ in range(num_objects):
                obj_name = random.choice(SUPPORTED_OBJECTS)
                objects.append(DetectedObject(
                    object=obj_name,
                    confidence=round(random.uniform(0.6, 0.98), 2),
                    bbox=[
                        random.randint(50, 150),
                        random.randint(50, 150),
                        random.randint(100, 200),
                        random.randint(150, 300)
                    ]
                ))
    
    return objects


def update_stats(detected_objects: List[DetectedObject], processing_time: int, risk: RiskLevel):
    """Update in-memory statistics."""
    global ANALYSIS_COUNT, TOTAL_OBJECTS
    
    ANALYSIS_COUNT += 1
    TOTAL_OBJECTS += len(detected_objects)
    PROCESSING_TIMES.append(processing_time)
    if len(PROCESSING_TIMES) > 1000:
        PROCESSING_TIMES.pop(0)
    
    for obj in detected_objects:
        OBJECT_COUNTS[obj.object] += 1
    
    RISK_COUNTS[risk.value] += 1


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    if isinstance(exc.detail, dict):
        problem = exc.detail
    else:
        problem = build_problem(
            status_code=exc.status_code,
            title="HTTP Error",
            detail=str(exc.detail),
            instance=str(request.url.path),
        )
    problem.setdefault("status", exc.status_code)
    problem.setdefault("type", "about:blank")
    return JSONResponse(
        status_code=exc.status_code,
        content=problem,
        media_type="application/problem+json",
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    first_error = exc.errors()[0] if exc.errors() else {}
    location = ".".join(str(item) for item in first_error.get("loc", []))
    message = first_error.get("msg", "Request validation error")
    detail = f"{location}: {message}" if location else message

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=build_problem(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            title="Validation error",
            detail=detail,
            instance=str(request.url.path),
            problem_type="https://smart-campus.local/problems/validation-error",
        ),
        media_type="application/problem+json",
    )


def verify_bearer_token(authorization: Optional[str] = Header(default=None)) -> None:
    """Verify bearer token for protected endpoints."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=build_problem(
                status_code=status.HTTP_401_UNAUTHORIZED,
                title="Unauthorized",
                detail="Missing Authorization header",
                problem_type="https://smart-campus.local/problems/unauthorized",
            ),
        )

    expected = f"Bearer {AUTH_TOKEN}"
    if authorization != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=build_problem(
                status_code=status.HTTP_401_UNAUTHORIZED,
                title="Unauthorized",
                detail="Invalid bearer token",
                problem_type="https://smart-campus.local/problems/unauthorized",
            ),
        )


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Public health check endpoint."""
    return HealthResponse(
        status="ok",
        service=SERVICE_NAME,
        version=SERVICE_VERSION,
    )


@app.post(
    "/vision/analyze",
    response_model=ImageAnalysisResponse,
    responses={
        200: {"model": ImageAnalysisResponse},
        400: {"model": ProblemDetails},
        401: {"model": ProblemDetails},
        500: {"model": ProblemDetails},
    },
)
def analyze_image(
    payload: ImageAnalysisRequest,
    authorization: Optional[str] = Header(default=None),
) -> ImageAnalysisResponse:
    """
    Analyze a single image using AI (YOLO or mock).
    
    This endpoint receives image data/url from Camera Stream service,
    performs object detection, and returns the results.
    """
    verify_bearer_token(authorization)
    
    # Validate input
    if not payload.image_url and not payload.image_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=build_problem(
                status_code=status.HTTP_400_BAD_REQUEST,
                title="Bad Request",
                detail="Either image_url or image_data is required",
                instance="/vision/analyze",
                problem_type="https://smart-campus.local/problems/bad-request",
            ),
        )
    
    start_time = time.time()
    
    # Mock AI detection (replace with real YOLO in production)
    detected_objects = mock_yolo_detection(payload.camera_id)
    
    # Calculate risk level
    risk_level, alert_triggered = calculate_risk_level(detected_objects)
    
    processing_time = int((time.time() - start_time) * 1000)
    
    # Update statistics
    update_stats(detected_objects, processing_time, risk_level)
    
    return ImageAnalysisResponse(
        detected=len(detected_objects) > 0,
        objects=detected_objects,
        risk_level=risk_level,
        alert_triggered=alert_triggered,
        processing_time_ms=processing_time,
        model_version="yolov8n-mock",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.post(
    "/vision/batch",
    response_model=BatchAnalysisResponse,
    responses={
        200: {"model": BatchAnalysisResponse},
        401: {"model": ProblemDetails},
    },
)
def batch_analyze(
    payload: BatchAnalysisRequest,
    authorization: Optional[str] = Header(default=None),
) -> BatchAnalysisResponse:
    """Analyze multiple images in a single request."""
    verify_bearer_token(authorization)
    
    start_time = time.time()
    results = []
    processed = 0
    failed = 0
    
    for image in payload.images:
        try:
            # Create analysis request
            req = ImageAnalysisRequest(
                camera_id=image.camera_id,
                image_url=image.image_url,
                image_data=image.image_data,
                timestamp=image.timestamp,
            )
            
            # Analyze image
            detected_objects = mock_yolo_detection(image.camera_id)
            risk_level, alert_triggered = calculate_risk_level(detected_objects)
            
            results.append(ImageAnalysisResponse(
                detected=len(detected_objects) > 0,
                objects=detected_objects,
                risk_level=risk_level,
                alert_triggered=alert_triggered,
                processing_time_ms=random.randint(50, 200),
                timestamp=datetime.now(timezone.utc).isoformat(),
            ))
            processed += 1
            
            update_stats(detected_objects, 0, risk_level)
        except Exception:
            failed += 1
    
    total_time = int((time.time() - start_time) * 1000)
    
    return BatchAnalysisResponse(
        results=results,
        total_images=len(payload.images),
        processed=processed,
        failed=failed,
        processing_time_ms=total_time,
    )


@app.get("/vision/objects", response_model=SupportedObjectsResponse)
def get_supported_objects() -> SupportedObjectsResponse:
    """Get list of supported object classes."""
    return SupportedObjectsResponse(
        objects=SUPPORTED_OBJECTS,
        model_name="yolov8n",
        model_version="8.0.0",
        detection_threshold=0.5,
    )


@app.get("/vision/stats", response_model=VisionStats)
def get_vision_stats(authorization: Optional[str] = Header(default=None)) -> VisionStats:
    """Get vision analysis statistics."""
    verify_bearer_token(authorization)
    
    avg_time = sum(PROCESSING_TIMES) / len(PROCESSING_TIMES) if PROCESSING_TIMES else 0
    
    # Top 5 objects
    top_objects = sorted(
        [{"object": k, "count": v} for k, v in OBJECT_COUNTS.items()],
        key=lambda x: x["count"],
        reverse=True
    )[:5]
    
    # Risk distribution
    risk_dist = {
        "low": RISK_COUNTS.get("low", 0),
        "medium": RISK_COUNTS.get("medium", 0),
        "high": RISK_COUNTS.get("high", 0),
        "critical": RISK_COUNTS.get("critical", 0),
    }
    
    return VisionStats(
        total_analyzed=ANALYSIS_COUNT,
        total_objects=TOTAL_OBJECTS,
        avg_processing_time_ms=round(avg_time, 2),
        top_objects=top_objects,
        risk_distribution=risk_dist,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
