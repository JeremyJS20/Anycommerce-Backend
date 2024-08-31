from datetime import datetime

from src.shared.generics import CommonModel
from src.utils.utils import ObjectIdTypeConverter


class SessionTokenDataModel(CommonModel):
    accessToken: str
    tokenType: str
    expiresIn: datetime
    refreshToken: str


class SessionTokenModel(CommonModel):
    id: ObjectIdTypeConverter
    username: str
    sessionDate: datetime
    data: SessionTokenDataModel
