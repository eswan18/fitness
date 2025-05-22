import tempfile
from datetime import date
from pathlib import Path
from typing import Iterator

import pytest

from fitness.ingest.mmf import MmfRun, load_mmf_data

FAKE_MMF_DATA = """Date Submitted,Workout Date,Activity Type,Calories Burned (kCal),Distance (mi),Workout Time (seconds),Avg Pace (min/mi),Max Pace (min/mi),Avg Speed (mi/h),Max Speed (mi/h),Avg Heart Rate,Steps,Notes,Source,Link
"May 6, 2025","May 6, 2025",Indoor Run / Jog,582,4.0,2036,8.48333,7.57699,7.07269,7.91871,146,5658,Shoes: Karhu Fusion 3.5,Map My Fitness MapMyRun iPhone,http://www.mapmyfitness.com/workout/8551842508
"May 5, 2025","May 5, 2025",Indoor Run / Jog,706,5.0,2364,7.88,7.75629,7.61421,7.73566,146,5327,Shoes: Karhu Fusion 3.5,Map My Fitness MapMyRun iPhone,http://www.mapmyfitness.com/workout/8550068398"""


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
    runs = load_mmf_data(mmf_file=mmf_datafile)
    assert len(runs) == 2
    assert isinstance(runs[0], MmfRun)
    assert runs[0].date_submitted == date(2025, 5, 6)
