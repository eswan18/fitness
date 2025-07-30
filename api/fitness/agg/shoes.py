from fitness.load import Run
from fitness.services.retirement import RetirementService


def mileage_by_shoes(
    runs: list[Run],
    include_retired: bool = False,
    retirement_service: RetirementService | None = None,
) -> dict[str, float]:
    """
    Calculate the total mileage for each pair of shoes used in the runs.

    Args:
        runs: List of runs to calculate mileage from
        include_retired: Whether to include retired shoes in the calculation
        retirement_service: Optional retirement service instance for testing
    """
    if retirement_service is None:
        retirement_service = RetirementService()
    mileage: dict[str, float] = {}

    for run in runs:
        if run.shoe_name is None:
            continue

        # Skip retired shoes if not including them
        if not include_retired and retirement_service.is_shoe_retired(run.shoe_name):
            continue

        mileage[run.shoe_name] = mileage.get(run.shoe_name, 0.0) + run.distance
    return mileage


def mileage_by_shoes_with_retirement(
    runs: list[Run], retirement_service: RetirementService | None = None
) -> dict[str, dict]:
    """
    Calculate mileage for all shoes with retirement information.

    Args:
        runs: List of runs to calculate mileage from
        retirement_service: Optional retirement service instance for testing

    Returns:
        Dict mapping shoe name to dict with mileage, retired status, and retirement info
    """
    if retirement_service is None:
        retirement_service = RetirementService()
    mileage: dict[str, float] = {}

    # Calculate mileage for all shoes (including retired)
    for run in runs:
        if run.shoe_name is None:
            continue
        mileage[run.shoe_name] = mileage.get(run.shoe_name, 0.0) + run.distance

    # Add retirement information
    result = {}
    for shoe_name, total_mileage in mileage.items():
        retirement_info = retirement_service.get_retirement_info(shoe_name)
        result[shoe_name] = {
            "mileage": total_mileage,
            "retired": retirement_info is not None,
            "retired_at": retirement_info.retired_at if retirement_info else None,
            "retirement_notes": retirement_info.retirement_notes if retirement_info else None,
        }

    return result
