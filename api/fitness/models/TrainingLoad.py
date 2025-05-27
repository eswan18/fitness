from datetime import date

from pydantic import BaseModel


class TrainingLoad(BaseModel):
    day: date
    atl: float
    ctl: float
    tsb: float
