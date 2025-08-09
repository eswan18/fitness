from .run import Run, RunType, RunSource, LocalizedRun
from .run_with_shoes import RunWithShoes
from .shoe import Shoe, ShoeMileage
from .training_load import TrainingLoad, DayTrainingLoad
from typing import Literal

Sex = Literal["M", "F"]


__all__ = [
    "Run",
    "RunType",
    "RunSource",
    "LocalizedRun",
    "RunWithShoes",
    "Shoe",
    "ShoeMileage",
    "TrainingLoad",
    "DayTrainingLoad",
    "Sex",
]
