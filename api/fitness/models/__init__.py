from .run import Run, RunType, RunSource
from .training_load import TrainingLoad, DayTrainingLoad
from typing import Literal

Sex = Literal["M", "F"]


__all__ = ["Run", "RunType", "RunSource", "TrainingLoad", "DayTrainingLoad", "Sex"]
