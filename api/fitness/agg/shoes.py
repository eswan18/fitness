from typing import Callable, Optional
from fitness.load import Run
from fitness.db.shoes import get_shoe_by_name
from fitness.models.shoe import Shoe


def mileage_by_shoes(
    runs: list[Run],
    include_retired: bool = False,
    get_shoe_fn: Optional[Callable[[str], Optional[Shoe]]] = None,
) -> dict[str, float]:
    """
    Calculate the total mileage for each pair of shoes used in the runs.

    Args:
        runs: List of runs to calculate mileage from
        include_retired: Whether to include retired shoes in the calculation
        get_shoe_fn: Optional function to get shoe by name (for testing)
    """
    if get_shoe_fn is None:
        get_shoe_fn = get_shoe_by_name
        
    mileage: dict[str, float] = {}

    for run in runs:
        if run.shoe_name is None:
            continue

        # Skip retired shoes if not including them
        if not include_retired:
            shoe = get_shoe_fn(run.shoe_name)
            if shoe and shoe.is_retired:
                continue

        mileage[run.shoe_name] = mileage.get(run.shoe_name, 0.0) + run.distance
    return mileage


def mileage_by_shoes_with_retirement(
    runs: list[Run], 
    get_shoe_fn: Optional[Callable[[str], Optional[Shoe]]] = None
) -> dict[str, dict]:
    """
    Calculate mileage for all shoes with retirement information.

    Args:
        runs: List of runs to calculate mileage from
        get_shoe_fn: Optional function to get shoe by name (for testing)

    Returns:
        Dict mapping shoe name to dict with mileage, retired status, and retirement info
    """
    if get_shoe_fn is None:
        get_shoe_fn = get_shoe_by_name
        
    mileage: dict[str, float] = {}

    # Calculate mileage for all shoes (including retired)
    for run in runs:
        if run.shoe_name is None:
            continue
        mileage[run.shoe_name] = mileage.get(run.shoe_name, 0.0) + run.distance

    # Add retirement information
    result = {}
    for shoe_name, total_mileage in mileage.items():
        shoe = get_shoe_fn(shoe_name)
        result[shoe_name] = {
            "mileage": total_mileage,
            "retired": shoe.is_retired if shoe else False,
            "retired_at": shoe.retired_at if shoe and shoe.is_retired else None,
            "retirement_notes": shoe.retirement_notes if shoe and shoe.is_retired else None,
        }

    return result
