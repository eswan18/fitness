from datetime import date

from fitness.agg.shoes import mileage_by_shoes, mileage_by_shoes_with_retirement


def test_mileage_by_shoes(run_factory):
    nikes = "Nike Air Zoom Pegasus 37"
    brooks = "Brooks Ghost 14"
    # Create shoes first to get their IDs
    from fitness.models.shoe import Shoe, generate_shoe_id
    brooks_id = generate_shoe_id(brooks)
    nikes_id = generate_shoe_id(nikes)
    
    shoes = [
        Shoe(id=brooks_id, name=brooks),
        Shoe(id=nikes_id, name=nikes),
    ]
    
    runs = [
        run_factory.make(update={"distance": 4.0, "shoe_id": brooks_id}),
        run_factory.make(update={"distance": 5.0, "shoe_id": nikes_id}),
        run_factory.make(update={"distance": 2.0, "shoe_id": None}),
        run_factory.make(update={"distance": 2.0, "shoe_id": None}),
        run_factory.make(update={"distance": 3.0, "shoe_id": nikes_id}),
        run_factory.make(update={"distance": 1.0, "shoe_id": brooks_id}),
    ]
    
    mileage = mileage_by_shoes(runs, shoes=shoes)
    assert mileage[brooks] == 5.0
    assert mileage[nikes] == 8.0


def test_mileage_by_shoes_exclude_retired(run_factory):
    """Test that retired shoes are excluded by default."""
    nikes = "Nike Air Zoom Pegasus 37"
    brooks = "Brooks Ghost 14"
    
    # Create mock shoes with nike retired and brooks active
    from fitness.models.shoe import Shoe, generate_shoe_id
    brooks_id = generate_shoe_id(brooks)
    nikes_id = generate_shoe_id(nikes)
    
    mock_shoes = [
        Shoe(
            id=nikes_id,
            name=nikes, 
            retired_at=date(2024, 12, 15),
            retirement_notes="Worn out"
        ),
        Shoe(id=brooks_id, name=brooks)  # Active shoe
    ]
    
    runs = [
        run_factory.make(update={"distance": 4.0, "shoe_id": brooks_id}),
        run_factory.make(update={"distance": 5.0, "shoe_id": nikes_id}),
        run_factory.make(update={"distance": 3.0, "shoe_id": nikes_id}),
        run_factory.make(update={"distance": 1.0, "shoe_id": brooks_id}),
    ]
    
    # Test without including retired (default behavior)
    mileage = mileage_by_shoes(
        runs, shoes=mock_shoes, include_retired=False
    )
    assert brooks in mileage
    assert nikes not in mileage  # Should be excluded
    assert mileage[brooks] == 5.0

    # Test with including retired
    mileage_with_retired = mileage_by_shoes(
        runs, shoes=mock_shoes, include_retired=True
    )
    assert brooks in mileage_with_retired
    assert nikes in mileage_with_retired  # Should be included
    assert mileage_with_retired[brooks] == 5.0
    assert mileage_with_retired[nikes] == 8.0


def test_mileage_by_shoes_with_retirement(run_factory):
    """Test mileage calculation with retirement information."""
    nikes = "Nike Air Zoom Pegasus 37"
    brooks = "Brooks Ghost 14"
    
    # Create mock shoes with nike retired and brooks active
    from fitness.models.shoe import Shoe, generate_shoe_id
    brooks_id = generate_shoe_id(brooks)
    nikes_id = generate_shoe_id(nikes)
    
    mock_shoes = [
        Shoe(
            id=nikes_id,
            name=nikes, 
            retired_at=date(2024, 12, 15),
            retirement_notes="Worn out"
        ),
        Shoe(id=brooks_id, name=brooks)  # Active shoe
    ]
    
    runs = [
        run_factory.make(update={"distance": 4.0, "shoe_id": brooks_id}),
        run_factory.make(update={"distance": 5.0, "shoe_id": nikes_id}),
        run_factory.make(update={"distance": 3.0, "shoe_id": nikes_id}),
        run_factory.make(update={"distance": 1.0, "shoe_id": brooks_id}),
    ]

    mileage_with_retirement = mileage_by_shoes_with_retirement(
        runs, shoes=mock_shoes
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
