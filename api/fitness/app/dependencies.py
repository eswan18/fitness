from functools import cache

from fitness.load import load_all_runs
from fitness.models import Run


@cache
def all_runs() -> list[Run]:
    return load_all_runs()
