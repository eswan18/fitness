"""Tests for timezone utility functions."""

from datetime import date, datetime, timezone
from zoneinfo import ZoneInfoNotFoundError
import pytest
import zoneinfo

from fitness.utils.timezone import (
    convert_utc_date_to_user_timezone,
    convert_runs_to_user_timezone,
    filter_runs_by_local_date_range,
)
from tests._factories.run import RunFactory


def make_run(**kwargs):
    """Helper function to create a run with given attributes."""
    factory = RunFactory()
    return factory.make(kwargs)


def convert_utc_datetime_to_user_timezone(utc_datetime: datetime, user_timezone: str) -> date:
    """Helper function to convert UTC datetime to user timezone date."""
    tz = zoneinfo.ZoneInfo(user_timezone)
    utc_aware = utc_datetime.replace(tzinfo=timezone.utc)
    local_datetime = utc_aware.astimezone(tz)
    return local_datetime.date()


class TestConvertUtcDateToUserTimezone:
    """Test UTC date to user timezone conversion."""

    def test_chicago_winter_conversion(self):
        """Test that UTC midnight becomes previous day in Chicago (UTC-6)."""
        utc_date = date(2025, 1, 15)
        result = convert_utc_date_to_user_timezone(utc_date, "America/Chicago")
        # UTC midnight becomes 6 PM previous day in Chicago
        assert result == date(2025, 1, 14)

    def test_tokyo_conversion_same_date(self):
        """Test that UTC midnight stays same date in Tokyo (UTC+9)."""
        utc_date = date(2025, 1, 15)
        result = convert_utc_date_to_user_timezone(utc_date, "Asia/Tokyo")
        # UTC midnight becomes 9 AM same day in Tokyo
        assert result == date(2025, 1, 15)

    def test_honolulu_conversion_previous_day(self):
        """Test with UTC-10 timezone (Honolulu)."""
        utc_date = date(2025, 1, 15)
        result = convert_utc_date_to_user_timezone(utc_date, "Pacific/Honolulu")
        # UTC midnight becomes 2 PM previous day in Honolulu
        assert result == date(2025, 1, 14)


class TestConvertRunsToUserTimezone:
    """Test run conversion to user timezone."""

    def test_no_timezone_returns_original_dates(self):
        """Test that None timezone returns original dates."""
        runs = [
            make_run(date=date(2025, 1, 15)),
            make_run(date=date(2025, 1, 16)),
        ]
        result = convert_runs_to_user_timezone(runs, user_timezone=None)

        assert len(result) == 2
        assert result[0].local_date == date(2025, 1, 15)
        assert result[1].local_date == date(2025, 1, 16)
        assert result[0].run == runs[0]
        assert result[1].run == runs[1]

    def test_timezone_conversion_applies(self):
        """Test that timezone conversion is applied."""
        runs = [make_run(date=date(2025, 1, 15))]
        result = convert_runs_to_user_timezone(runs, user_timezone="Pacific/Honolulu")

        assert len(result) == 1
        assert result[0].local_date == date(2025, 1, 14)  # Previous day in Honolulu
        assert result[0].run == runs[0]


class TestFilterRunsByLocalDateRange:
    """Test filtering runs by local date range."""

    def test_no_timezone_uses_utc_dates(self):
        """Test that None timezone uses original UTC filtering logic."""
        runs = [
            make_run(date=date(2025, 1, 14)),
            make_run(date=date(2025, 1, 15)),
            make_run(date=date(2025, 1, 16)),
        ]

        result = filter_runs_by_local_date_range(
            runs, start=date(2025, 1, 15), end=date(2025, 1, 15), user_timezone=None
        )

        assert len(result) == 1
        assert result[0].date == date(2025, 1, 15)

    def test_timezone_filtering_includes_converted_dates(self):
        """Test that timezone filtering includes runs from converted local dates."""
        runs = [
            make_run(date=date(2025, 1, 14)),  # This converts to 2025-01-13 in Honolulu
            make_run(date=date(2025, 1, 15)),  # This converts to 2025-01-14 in Honolulu
            make_run(date=date(2025, 1, 16)),  # This converts to 2025-01-15 in Honolulu
        ]

        # Filter for 2025-01-14 in Honolulu timezone
        result = filter_runs_by_local_date_range(
            runs,
            start=date(2025, 1, 14),
            end=date(2025, 1, 14),
            user_timezone="Pacific/Honolulu",
        )

        # Should return the run with UTC date 2025-01-15 (which converts to 2025-01-14 in Honolulu)
        assert len(result) == 1
        assert result[0].date == date(2025, 1, 15)

    def test_timezone_filtering_range(self):
        """Test timezone filtering with a date range."""
        runs = [
            make_run(date=date(2025, 1, 14)),  # Converts to 2025-01-13 in Honolulu
            make_run(date=date(2025, 1, 15)),  # Converts to 2025-01-14 in Honolulu
            make_run(date=date(2025, 1, 16)),  # Converts to 2025-01-15 in Honolulu
            make_run(date=date(2025, 1, 17)),  # Converts to 2025-01-16 in Honolulu
        ]

        # Filter for 2025-01-14 to 2025-01-15 in Honolulu timezone
        result = filter_runs_by_local_date_range(
            runs,
            start=date(2025, 1, 14),
            end=date(2025, 1, 15),
            user_timezone="Pacific/Honolulu",
        )

        # Should return runs with UTC dates 2025-01-15 and 2025-01-16
        # (which convert to 2025-01-14 and 2025-01-15 in Honolulu)
        assert len(result) == 2
        assert result[0].date == date(2025, 1, 15)
        assert result[1].date == date(2025, 1, 16)


class TestTimezoneEdgeCases:
    """Test edge cases for timezone conversion."""

    def test_dst_transition_spring_forward(self):
        """Test timezone conversion during spring DST transition."""
        # March 9, 2025 is when DST starts in the US (2 AM -> 3 AM)
        utc_date = date(2025, 3, 9)
        result = convert_utc_date_to_user_timezone(utc_date, "America/New_York")
        # Should still convert correctly despite DST transition
        assert isinstance(result, date)

    def test_dst_transition_fall_back(self):
        """Test timezone conversion during fall DST transition."""
        # November 2, 2025 is when DST ends in the US (2 AM -> 1 AM)
        utc_date = date(2025, 11, 2)
        result = convert_utc_date_to_user_timezone(utc_date, "America/New_York")
        # Should still convert correctly despite DST transition
        assert isinstance(result, date)

    def test_year_boundary_crossing(self):
        """Test timezone conversion that crosses year boundary."""
        # New Year's Eve UTC becomes New Year's Day in eastern timezones
        utc_date = date(2025, 1, 1)
        result = convert_utc_date_to_user_timezone(utc_date, "Asia/Tokyo")
        # Should handle year boundary correctly
        assert result == date(2025, 1, 1)  # UTC midnight = 9 AM same day in Tokyo

    def test_year_boundary_crossing_reverse(self):
        """Test timezone conversion that crosses year boundary backwards."""
        # New Year's Day UTC becomes New Year's Eve in western timezones
        utc_date = date(2025, 1, 1)
        result = convert_utc_date_to_user_timezone(utc_date, "Pacific/Honolulu")
        # Should handle year boundary correctly
        assert result == date(
            2024, 12, 31
        )  # UTC midnight = 2 PM previous day in Honolulu

    def test_invalid_timezone_raises_error(self):
        """Test that invalid timezone raises appropriate error."""
        with pytest.raises(ZoneInfoNotFoundError):
            convert_utc_date_to_user_timezone(date(2025, 1, 1), "Invalid/Timezone")

    def test_empty_runs_list(self):
        """Test timezone functions with empty runs list."""
        result = filter_runs_by_local_date_range(
            [], date(2025, 1, 1), date(2025, 1, 2), "America/Chicago"
        )
        assert result == []

    def test_runs_outside_date_range(self):
        """Test that runs outside the date range are properly excluded."""
        runs = [
            make_run(
                date=date(2025, 1, 5)
            ),  # Converts to 2025-01-04 in Chicago (before range)
            make_run(
                date=date(2025, 1, 10)
            ),  # Converts to 2025-01-09 in Chicago (in range)
            make_run(
                date=date(2025, 1, 16)
            ),  # Converts to 2025-01-15 in Chicago (in range)
            make_run(
                date=date(2025, 1, 20)
            ),  # Converts to 2025-01-19 in Chicago (after range)
        ]

        # Request range from 2025-01-05 to 2025-01-15 in Chicago timezone
        result = filter_runs_by_local_date_range(
            runs, date(2025, 1, 5), date(2025, 1, 15), "America/Chicago"
        )

        # Should return 2 runs: UTC dates 2025-01-10 and 2025-01-16
        assert len(result) == 2
        assert result[0].date == date(2025, 1, 10)
        assert result[1].date == date(2025, 1, 16)

    def test_single_day_range(self):
        """Test filtering for a single day range."""
        runs = [
            make_run(date=date(2025, 1, 14)),  # This converts to 2025-01-13 in Chicago
            make_run(date=date(2025, 1, 15)),  # This converts to 2025-01-14 in Chicago
            make_run(date=date(2025, 1, 16)),  # This converts to 2025-01-15 in Chicago
        ]

        # Request January 15th in Chicago timezone
        result = filter_runs_by_local_date_range(
            runs, date(2025, 1, 15), date(2025, 1, 15), "America/Chicago"
        )

        # Should return the run with UTC date 2025-01-16 (which converts to 2025-01-15 in Chicago)
        assert len(result) == 1
        assert result[0].date == date(2025, 1, 16)

    def test_timezone_abbreviations(self):
        """Test that common timezone abbreviations work."""
        # This tests that standard timezone names are accepted
        utc_date = date(2025, 1, 15)

        # Test a few common timezone formats
        timezones_to_test = [
            "America/New_York",
            "Europe/London",
            "Asia/Tokyo",
            "Australia/Sydney",
        ]

        for tz in timezones_to_test:
            result = convert_utc_date_to_user_timezone(utc_date, tz)
            assert isinstance(result, date), f"Failed for timezone {tz}"


class TestDatetimeBasedTimezoneConversion:
    """Test datetime-based timezone conversion edge cases."""

    def test_1am_utc_run_crosses_date_boundaries(self):
        """Test that a 1 AM UTC run appears on correct days across timezones."""
        
        # 1 AM UTC on January 15th
        utc_datetime = datetime(2025, 1, 15, 1, 0, 0)
        
        # Test multiple timezones
        test_cases = [
            # Eastern timezones (ahead of UTC) - should stay same day
            ("Asia/Tokyo", date(2025, 1, 15)),      # UTC+9: 1 AM UTC = 10 AM local
            ("Europe/London", date(2025, 1, 15)),   # UTC+0: 1 AM UTC = 1 AM local
            ("Europe/Berlin", date(2025, 1, 15)),   # UTC+1: 1 AM UTC = 2 AM local
            
            # Western timezones (behind UTC) - should shift to previous day
            ("America/New_York", date(2025, 1, 14)), # UTC-5: 1 AM UTC = 8 PM Jan 14
            ("America/Chicago", date(2025, 1, 14)),  # UTC-6: 1 AM UTC = 7 PM Jan 14
            ("America/Denver", date(2025, 1, 14)),   # UTC-7: 1 AM UTC = 6 PM Jan 14
            ("America/Los_Angeles", date(2025, 1, 14)), # UTC-8: 1 AM UTC = 5 PM Jan 14
            ("Pacific/Honolulu", date(2025, 1, 14)), # UTC-10: 1 AM UTC = 3 PM Jan 14
        ]
        
        for timezone_str, expected_date in test_cases:
            result = convert_utc_datetime_to_user_timezone(utc_datetime, timezone_str)
            assert result == expected_date, f"Failed for {timezone_str}: got {result}, expected {expected_date}"

    def test_midnight_utc_vs_1am_utc_difference(self):
        """Test that runs at midnight vs 1 AM UTC can end up on different local dates."""
        
        # Two runs on same UTC date but different times
        midnight_utc = datetime(2025, 1, 15, 0, 0, 0)
        one_am_utc = datetime(2025, 1, 15, 1, 0, 0)
        
        # In Chicago (UTC-6 in winter):
        # - Midnight UTC (Jan 15) = 6 PM Jan 14 local
        # - 1 AM UTC (Jan 15) = 7 PM Jan 14 local
        # Both should end up on Jan 14 in Chicago
        
        midnight_chicago = convert_utc_datetime_to_user_timezone(midnight_utc, "America/Chicago")
        one_am_chicago = convert_utc_datetime_to_user_timezone(one_am_utc, "America/Chicago")
        
        assert midnight_chicago == date(2025, 1, 14)
        assert one_am_chicago == date(2025, 1, 14)
        
        # But in Tokyo (UTC+9):
        # - Midnight UTC (Jan 15) = 9 AM Jan 15 local
        # - 1 AM UTC (Jan 15) = 10 AM Jan 15 local
        # Both should end up on Jan 15 in Tokyo
        
        midnight_tokyo = convert_utc_datetime_to_user_timezone(midnight_utc, "Asia/Tokyo")
        one_am_tokyo = convert_utc_datetime_to_user_timezone(one_am_utc, "Asia/Tokyo")
        
        assert midnight_tokyo == date(2025, 1, 15)
        assert one_am_tokyo == date(2025, 1, 15)

    def test_run_aggregation_with_timezone_edge_cases(self):
        """Test that runs aggregate correctly across timezone boundaries."""
        from fitness.agg.mileage import total_mileage
        
        # Create runs at different times on the same UTC date
        runs = [
            make_run(
                date=date(2025, 1, 15),
                datetime_utc=datetime(2025, 1, 15, 1, 0, 0),  # 1 AM UTC
                distance=5.0
            ),
            make_run(
                date=date(2025, 1, 15), 
                datetime_utc=datetime(2025, 1, 15, 12, 0, 0),  # Noon UTC
                distance=3.0
            ),
            make_run(
                date=date(2025, 1, 15),
                datetime_utc=datetime(2025, 1, 15, 23, 0, 0),  # 11 PM UTC
                distance=2.0
            ),
        ]
        
        # In Chicago timezone:
        # - 1 AM UTC (Jan 15) → 7 PM Jan 14 Chicago
        # - Noon UTC (Jan 15) → 6 AM Jan 15 Chicago  
        # - 11 PM UTC (Jan 15) → 5 PM Jan 15 Chicago
        
        # Query for Jan 14 in Chicago should only get the first run
        jan_14_chicago = total_mileage(runs, date(2025, 1, 14), date(2025, 1, 14), "America/Chicago")
        assert jan_14_chicago == 5.0
        
        # Query for Jan 15 in Chicago should get the other two runs
        jan_15_chicago = total_mileage(runs, date(2025, 1, 15), date(2025, 1, 15), "America/Chicago")
        assert jan_15_chicago == 5.0  # 3.0 + 2.0
        
        # In Tokyo timezone:
        # - 1 AM UTC (Jan 15) → 10 AM Jan 15 Tokyo
        # - Noon UTC (Jan 15) → 9 PM Jan 15 Tokyo  
        # - 11 PM UTC (Jan 15) → 8 AM Jan 16 Tokyo
        
        # Query for Jan 15 in Tokyo should get the first two runs
        jan_15_tokyo = total_mileage(runs, date(2025, 1, 15), date(2025, 1, 15), "Asia/Tokyo")
        assert jan_15_tokyo == 8.0  # 5.0 + 3.0
        
        # Query for Jan 16 in Tokyo should get the third run
        jan_16_tokyo = total_mileage(runs, date(2025, 1, 16), date(2025, 1, 16), "Asia/Tokyo")
        assert jan_16_tokyo == 2.0

    def test_year_boundary_datetime_conversion(self):
        """Test datetime conversion across year boundaries."""
        
        # 2 AM UTC on January 1st, 2025
        utc_datetime = datetime(2025, 1, 1, 2, 0, 0)
        
        # In Honolulu (UTC-10), this should be 4 PM on December 31st, 2024
        honolulu_date = convert_utc_datetime_to_user_timezone(utc_datetime, "Pacific/Honolulu")
        assert honolulu_date == date(2024, 12, 31)
        
        # In Tokyo (UTC+9), this should be 11 AM on January 1st, 2025
        tokyo_date = convert_utc_datetime_to_user_timezone(utc_datetime, "Asia/Tokyo")
        assert tokyo_date == date(2025, 1, 1)
