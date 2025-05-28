from datetime import date, timedelta
import math

from fitness.models import Run, DayTrainingLoad, TrainingLoad, Sex

ATL_LOOKBACK = 7
CTL_LOOKBACK = 42


def _trimp(run: Run, max_hr: float, resting_hr: float, sex: Sex) -> float:
    """
    Calculate the Banister TRaining IMPulse score for a run.

    TRIMP = Duration (minutes) x HR_Relative x Y
    where HR_Relative is the relative heart rate:
        - HR_Relative = (avg_hr_during_for_activity - resting_hr) / (max_hr - resting_hr)
    where Y is a sex-based weighting factor:
        - For men: Y = 0.64 * e^(1.92 x HR_Relative)
        - For women: Y = 0.86 * e^(1.67 x HR_Relative)
    """
    if run.avg_heart_rate is None:
        raise ValueError("Run must have an average heart rate to calculate TRIMP.")
    hr_relative = (run.avg_heart_rate - resting_hr) / (max_hr - resting_hr)
    # Clamp hr_relative to the range [0, 1]
    hr_relative = max(0.0, min(1.0, hr_relative))
    match sex:
        case "M":
            y = 0.64 * math.exp(1.92 * hr_relative)
        case "F":
            y = 0.86 * math.exp(1.67 * hr_relative)
    duration_minutes = run.duration / 60
    return duration_minutes * hr_relative * y


def _exponential_training_load(trimp_values: list[float], tau: int) -> list[float]:
    alpha = 1 - math.exp(-1 / tau)
    load = []
    prev = 0.0
    for trimp in trimp_values:
        current = prev + alpha * (trimp - prev)
        load.append(current)
        prev = current
    return load


def _calculate_atl_and_ctl(
    trimp_values: list[float],
) -> tuple[list[float], list[float]]:
    """
    Calculate Acute Training Load (ATL) and Chronic Training Load (CTL).

    The ATL is calculated over a 7-day lookback period, and the CTL is calculated over a 42-day lookback period.
    """
    atl_values = _exponential_training_load(trimp_values, ATL_LOOKBACK)
    ctl_values = _exponential_training_load(trimp_values, CTL_LOOKBACK)
    return atl_values, ctl_values


def training_stress_balance(
    runs: list[Run],
    max_hr: float,
    resting_hr: float,
    sex: Sex,
    start_date: date,
    end_date: date,
) -> list[DayTrainingLoad]:
    """
    Calculate Training Stress Balance (TSB) as the difference between CTL and ATL.
    """
    # Filter runs to only those with a valid average heart rate.
    runs = [run for run in runs if run.avg_heart_rate is not None]
    trimp_by_date: list[tuple[date, float]] = []
    # TODO: start max(CTL_LOOKBACK, ATL_LOOKBACK) days before start_date
    # to ensure we have enough data for the initial ATL and CTL calculations.
    for i in range((end_date - start_date).days + 1):
        current_date = start_date + timedelta(days=i)
        runs_for_day = [run for run in runs if run.date == current_date]
        trimp_values = [_trimp(run, max_hr, resting_hr, sex) for run in runs_for_day]
        trimp_by_date.append((current_date, sum(trimp_values, start=0.0)))
    atl, ctl = _calculate_atl_and_ctl([trimp for _, trimp in trimp_by_date])
    tsb = [ctl_value - atl_value for ctl_value, atl_value in zip(ctl, atl)]
    dates = [dt for dt, _ in trimp_by_date]
    return [
        DayTrainingLoad(date=d, training_load=TrainingLoad(ctl=c, atl=a, tsb=t))
        for (d, c, a, t) in zip(dates, ctl, atl, tsb)
    ]
