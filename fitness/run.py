from datetime import datetime
from dataclasses import dataclass


@dataclass
class Run:
    start_time: datetime
    distance: float
    duration: float
    average_speed: float
    shoes: str
