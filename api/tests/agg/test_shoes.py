import tempfile
from datetime import date
from pathlib import Path

from fitness.agg.shoes import mileage_by_shoes, mileage_by_shoes_with_retirement
from fitness.services.retirement import RetirementService


def test_mileage_by_shoes(run_factory):
    nikes = "Nike Air Zoom Pegasus 37"
    brooks = "Brooks Ghost 14"
    runs = [
        run_factory.make(update={"distance": 4.0, "shoes": brooks}),
        run_factory.make(update={"distance": 5.0, "shoes": nikes}),
        run_factory.make(update={"distance": 2.0, "shoes": None}),
        run_factory.make(update={"distance": 2.0, "shoes": None}),
        run_factory.make(update={"distance": 3.0, "shoes": nikes}),
        run_factory.make(update={"distance": 1.0, "shoes": brooks}),
    ]

    mileage = mileage_by_shoes(runs)
    assert mileage[brooks] == 5.0
    assert mileage[nikes] == 8.0


def test_mileage_by_shoes_exclude_retired(run_factory):
    """Test that retired shoes are excluded by default."""
    nikes = "Nike Air Zoom Pegasus 37"
    brooks = "Brooks Ghost 14"
    runs = [
        run_factory.make(update={"distance": 4.0, "shoes": brooks}),
        run_factory.make(update={"distance": 5.0, "shoes": nikes}),
        run_factory.make(update={"distance": 3.0, "shoes": nikes}),
        run_factory.make(update={"distance": 1.0, "shoes": brooks}),
    ]

    # Create temporary retirement file and retire Nike shoes
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        config_path = Path(f.name)
        f.write("{}")  # Initialize with empty JSON
        f.flush()

    try:
        retirement_service = RetirementService()
        retirement_service.retire_shoe(nikes, date(2024, 12, 15))

        # Test without including retired (default behavior)
        mileage = mileage_by_shoes(
            runs, include_retired=False, retirement_service=retirement_service
        )
        assert brooks in mileage
        assert nikes not in mileage  # Should be excluded
        assert mileage[brooks] == 5.0

        # Test with including retired
        mileage_with_retired = mileage_by_shoes(
            runs, include_retired=True, retirement_service=retirement_service
        )
        assert brooks in mileage_with_retired
        assert nikes in mileage_with_retired  # Should be included
        assert mileage_with_retired[brooks] == 5.0
        assert mileage_with_retired[nikes] == 8.0

    finally:
        if config_path.exists():
            config_path.unlink()


def test_mileage_by_shoes_with_retirement(run_factory):
    """Test mileage calculation with retirement information."""
    nikes = "Nike Air Zoom Pegasus 37"
    brooks = "Brooks Ghost 14"
    runs = [
        run_factory.make(update={"distance": 4.0, "shoes": brooks}),
        run_factory.make(update={"distance": 5.0, "shoes": nikes}),
        run_factory.make(update={"distance": 3.0, "shoes": nikes}),
        run_factory.make(update={"distance": 1.0, "shoes": brooks}),
    ]

    # Create temporary retirement file and retire Nike shoes
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        config_path = Path(f.name)
        f.write("{}")  # Initialize with empty JSON
        f.flush()

    try:
        retirement_service = RetirementService()
        retirement_service.retire_shoe(nikes, date(2024, 12, 15), "Worn out")

        mileage_with_retirement = mileage_by_shoes_with_retirement(
            runs, retirement_service=retirement_service
        )

        # Check Nike shoes (retired)
        nike_info = mileage_with_retirement[nikes]
        assert nike_info["mileage"] == 8.0
        assert nike_info["retired"] is True
        assert nike_info["retired_at"] == date(2024, 12, 15)
        assert nike_info["retirement_notes"] == "Worn out"

        # Check Brooks shoes (not retired)
        brooks_info = mileage_with_retirement[brooks]
        assert brooks_info["mileage"] == 5.0
        assert brooks_info["retired"] is False
        assert brooks_info["retired_at"] is None
        assert brooks_info["retirement_notes"] is None

    finally:
        if config_path.exists():
            config_path.unlink()
