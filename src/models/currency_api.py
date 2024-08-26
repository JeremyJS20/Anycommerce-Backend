from datetime import datetime
from typing import Optional, Dict

from pydantic import Field

from src.shared.generics import CommonModel


class CurrencyConvertionRatesModel(CommonModel):
    baseCurrency: str
    lastUpdate: datetime
    nextUpdate: datetime
    convertionRates: Dict
