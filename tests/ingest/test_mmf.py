import tempfile
from datetime import date
from pathlib import Path
from typing import Iterator

import pytest

from fitness.ingest.mmf import MmfActivity, load_mmf_data, load_mmf_runs

# 4 sample runs from Map My Fitness, with a header. 3 runs, 1 bike ride.
FAKE_MMF_DATA = """Date Submitted,Workout Date,Activity Type,Calories Burned (kCal),Distance (mi),Workout Time (seconds),Avg Pace (min/mi),Max Pace (min/mi),Avg Speed (mi/h),Max Speed (mi/h),Avg Heart Rate,Steps,Notes,Source,Link
"May 6, 2025","May 6, 2025",Indoor Run / Jog,582,4.0,2036,8.48333,7.57699,7.07269,7.91871,146,5658,Shoes: Karhu Fusion 3.5,Map My Fitness MapMyRun iPhone,http://www.mapmyfitness.com/workout/8551842508
"May 5, 2025","May 5, 2025",Indoor Run / Jog,706,5.0,2364,7.88,7.75629,7.61421,7.73566,146,5327,Shoes: Karhu Fusion 3.5,Map My Fitness MapMyRun iPhone,http://www.mapmyfitness.com/workout/8550068398
"June 4, 2022","June 4, 2022",Bike Ride,348,7.59992,2815,6.1733,0.410257,9.71928,146.25,93,,,Map My Fitness MapMyRun iPhone,http://www.mapmyfitness.com/workout/6624154843
"March 7, 2016","March 7, 2016",Run,823,5.61139,2920,8.67284,5.91301,6.91815,10.1471,,11899,,Map My Fitness MapMyRun Android,http://www.mapmyfitness.com/workout/1374173327"""


@pytest.fixture(scope="session")
def mmf_datafile() -> Iterator[Path]:
    """Create a temporary file with fake MMF data."""
    # Create a temporary file with fake MMF data.
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv") as f:
        f.write(FAKE_MMF_DATA)
        f.flush()
        yield Path(f.name)


def test_load_mmf_data(mmf_datafile: Path):
    """Test that we can load the MMF data."""
    records = load_mmf_data(mmf_file=mmf_datafile)
    assert len(records) == 4
    assert isinstance(records[0], MmfActivity)
    assert records[0].date_submitted == date(2025, 5, 6)
    assert records[0].workout_date == date(2025, 5, 6)
    assert records[3].workout_date == date(2016, 3, 7)
    assert records[0].activity_type == "Indoor Run / Jog"
    assert records[2].activity_type == "Bike Ride"


def test_load_mmf_runs(mmf_datafile: Path):
    """Test that we can load the MMF data and filter to runs."""
    runs = load_mmf_runs(mmf_file=mmf_datafile)
    # Only 3 runs in the data; we excluded the bike ride.
    assert len(runs) == 3
    assert isinstance(runs[0], MmfActivity)
    assert runs[0].activity_type == "Indoor Run / Jog"
    assert runs[2].activity_type == "Run"


def test_mmf_run_shoes(mmf_datafile: Path):
    """Test that we can extract the shoes from the notes field."""
    runs = load_mmf_data(mmf_file=mmf_datafile)
    assert runs[0].shoes() == "Karhu Fusion 3.5"
    assert runs[2].shoes() is None
