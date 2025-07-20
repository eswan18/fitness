"""Timezone utility functions for converting between UTC and user timezones."""

from datetime import date, datetime, timezone
import zoneinfo
from typing import NamedTuple

from fitness.models import Run


class UserTimezoneRun(NamedTuple):
    """A run with its date converted to user's local timezone."""

    run: Run
    local_date: date




def convert_runs_to_user_timezone(
    runs: list[Run], user_timezone: str | None = None
) -> list[UserTimezoneRun]:
    """
    Convert a list of runs to use the user's local timezone for date bucketing.

    Uses the run's datetime_utc field for accurate timezone conversion.
    If user_timezone is None, returns runs with their original UTC dates.
    """
    if user_timezone is None:
        # No conversion needed - use original UTC dates
        return [UserTimezoneRun(run=run, local_date=run.datetime_utc.date()) for run in runs]

    tz = zoneinfo.ZoneInfo(user_timezone)
    result = []
    for run in runs:
        # Convert UTC datetime to user's local timezone date
        utc_aware = run.datetime_utc.replace(tzinfo=timezone.utc)
        local_datetime = utc_aware.astimezone(tz)
        local_date = local_datetime.date()
        result.append(UserTimezoneRun(run=run, local_date=local_date))

    return result


def filter_runs_by_local_date_range(
    runs: list[Run], start: date, end: date, user_timezone: str | None = None
) -> list[Run]:
    """
    Filter runs to only include those that fall within the date range in the user's timezone.

    If user_timezone is None, uses UTC dates (existing behavior).
    """
    if user_timezone is None:
        # Existing behavior - filter by UTC dates
        return [run for run in runs if start <= run.datetime_utc.date() <= end]

    # Convert runs to user timezone and filter by local dates
    user_tz_runs = convert_runs_to_user_timezone(runs, user_timezone)
    return [tz_run.run for tz_run in user_tz_runs if start <= tz_run.local_date <= end]
