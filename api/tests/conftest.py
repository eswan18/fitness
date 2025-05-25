import pytest


from ._factories import RunFactory, StravaActivityWithGearFactory, MmfActivityFactory


@pytest.fixture(scope="session")
def run_factory() -> RunFactory:
    return RunFactory()


@pytest.fixture(scope="session")
def strava_activity_with_gear_factory() -> StravaActivityWithGearFactory:
    return StravaActivityWithGearFactory()


@pytest.fixture(scope="session")
def mmf_activity_factory() -> MmfActivityFactory:
    return MmfActivityFactory()
