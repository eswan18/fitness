from pydantic import BaseModel


class TrainingLoad(BaseModel):
    atl: float
    ctl: float
    tsb: float
