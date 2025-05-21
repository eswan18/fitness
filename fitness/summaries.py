from dataclasses import dataclass


@dataclass
class Summary:
    # Making count a float instead of an int gives us the flexibility to use it for averages, etc.
    count: float
    miles: float
    runs: int
    minutes: float
    calories: float


def totals(df) -> Summary:
    """Calculate the total miles and runs."""
    return Summary(
        count=df.shape[0],
        miles=df["Distance (mi)"].sum(),
        runs=df["Distance (mi)"].count(),
        minutes=df["Workout Time (seconds)"].sum() / 60,
        calories=df["Calories Burned (kCal)"].sum(),
    )
