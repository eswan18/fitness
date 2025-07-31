from .run import Run, RunType, RunSource, LocalizedRun
from .shoe import Shoe, ShoeMileage
from .training_load import TrainingLoad, DayTrainingLoad
from typing import Literal

Sex = Literal["M", "F"]


__all__ = [
    "Run", 
    "RunType", 
    "RunSource", 
    "LocalizedRun",
    "Shoe",
    "ShoeMileage",
    "TrainingLoad", 
    "DayTrainingLoad",
    "Literal"
]
