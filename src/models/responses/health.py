from datetime import datetime
from src.shared.generics import CommonResponseModel

class HealthResponse(CommonResponseModel):
    status: str
    timestamp: datetime
    version: str
