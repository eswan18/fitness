from fitness.agg.shoes import mileage_by_shoes


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
