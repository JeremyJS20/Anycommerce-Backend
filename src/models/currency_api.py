from datetime import datetime
from typing import Dict, Optional

from src.shared.generics import CommonModel
from src.utils.utils import ObjectIdTypeConverter


class CurrencyConvertionRatesModel(CommonModel):
    id: ObjectIdTypeConverter
    baseCurrency: str
    lastUpdate: datetime
    nextUpdate: datetime
    convertionRates: Dict
