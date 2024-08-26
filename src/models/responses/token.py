from datetime import datetime

from src.shared.generics import CommonModel


class TokenResponse(CommonModel):
    accessToken: str
    tokenType: str
    expiresIn: datetime
    refreshToken: str
