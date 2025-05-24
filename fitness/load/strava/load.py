from .client import StravaClient
from .models import StravaActivityWithGear


def load_strava_runs() -> list[StravaActivityWithGear]:
    """Fetch runs from Strava along with the gear used in them."""
    client = StravaClient.from_env()
    # Get activities and the gear used in them.
    activities = client.get_activities()
    # Limit down to only runs.
    runs = [
        activity for activity in activities if activity.type in ("Run", "Indoor Run")
    ]
    gear_ids = {run.gear_id for run in runs if run.gear_id}
    gear = client.get_gear(gear_ids)
    gear_by_id = {g.id: g for g in gear}
    runs_w_gear = [
        run.with_gear(gear=gear_by_id.get(run.gear_id))
        for run in runs
        if run.gear_id is not None
    ]
    return runs_w_gear
