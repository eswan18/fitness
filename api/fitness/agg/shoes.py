from fitness.load import Run
from fitness.models.shoe import Shoe


def mileage_by_shoes(
    runs: list[Run],
    shoes: list[Shoe],
    include_retired: bool = False,
) -> dict[str, float]:
    """
    Calculate the total mileage for each pair of shoes used in the runs.

    Args:
        runs: List of runs to calculate mileage from
        shoes: List of all shoes to check retirement status against
        include_retired: Whether to include retired shoes in the calculation
    """
    # Create lookup dicts for shoes by ID and name
    shoe_id_lookup = {shoe.id: shoe for shoe in shoes}
    shoe_name_lookup = {shoe.id: shoe.name for shoe in shoes}
    
    mileage: dict[str, float] = {}

    for run in runs:
        if run.shoe_id is None:
            continue

        # Skip retired shoes if not including them
        if not include_retired:
            shoe = shoe_id_lookup.get(run.shoe_id)
            if shoe and shoe.is_retired:
                continue

        # Use shoe name for the result key (for backward compatibility)
        shoe_name = shoe_name_lookup.get(run.shoe_id)
        if shoe_name:
            mileage[shoe_name] = mileage.get(shoe_name, 0.0) + run.distance
    
    return mileage


def mileage_by_shoes_with_retirement(
    runs: list[Run], 
    shoes: list[Shoe]
) -> dict[str, dict]:
    """
    Calculate mileage for all shoes with retirement information.

    Args:
        runs: List of runs to calculate mileage from
        shoes: List of all shoes to get retirement information from

    Returns:
        Dict mapping shoe name to dict with mileage, retired status, and retirement info
    """
    # Create lookup dicts for shoes by ID and name
    shoe_id_lookup = {shoe.id: shoe for shoe in shoes}
    shoe_name_lookup = {shoe.id: shoe.name for shoe in shoes}
        
    mileage: dict[str, float] = {}

    # Calculate mileage for all shoes (including retired)
    for run in runs:
        if run.shoe_id is None:
            continue
        
        # Use shoe name for the result key (for backward compatibility)
        shoe_name = shoe_name_lookup.get(run.shoe_id)
        if shoe_name:
            mileage[shoe_name] = mileage.get(shoe_name, 0.0) + run.distance

    # Add retirement information
    result = {}
    for shoe_name, total_mileage in mileage.items():
        # Find the shoe by looking through all shoes for matching name
        shoe = next((s for s in shoes if s.name == shoe_name), None)
        result[shoe_name] = {
            "mileage": total_mileage,
            "retired": shoe.is_retired if shoe else False,
            "retired_at": shoe.retired_at if shoe and shoe.is_retired else None,
            "retirement_notes": shoe.retirement_notes if shoe and shoe.is_retired else None,
        }

    return result
