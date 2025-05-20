from .client import StravaClient


def pull_data() -> pd.DataFrame:
    """Pull the data from the Strava API."""
    client = StravaClient.from_env()

    activities = client.get_activities()
    gear_ids = set(a.gear.id for a in activities if a.gear is not None)
    gear = client.get_gear(gear_ids)
    # Turn the gear into a mapping from ID to nickname.
    gear_map = {row["id"]: row["nickname"] for _, row in gear.iterrows()}
    # Add a "Shoes" column to the activities dataframe.
    activities["shoes"] = activities["gear_id"].map(gear_map)
    activities = activities.drop(columns=["gear_id"])
    return activities
