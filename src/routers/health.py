from datetime import datetime
from fastapi import APIRouter, status
from src.models.responses.health import HealthResponse
from src.shared.generics import Data

health_router = APIRouter(tags=['Health'])

@health_router.get('', responses={
    status.HTTP_200_OK: {"model": Data[HealthResponse], 'description': 'Service is healthy'},
}, status_code=status.HTTP_200_OK)
def check_health():
    return Data[HealthResponse](
        data=HealthResponse(
            status="OK",
            timestamp=datetime.now(),
            version="1.0.0"
        )
    )
