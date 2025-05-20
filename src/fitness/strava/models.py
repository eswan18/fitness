from pydantic import BaseModel

class StravaActivity(BaseModel):
    id: int
    name: str
    type: str
    start_date: str
    start_date_local: str
    timezone: str
    utc_offset: int
    distance: float
    moving_time: int
    elapsed_time: int
    total_elevation_gain: float
    elevation_high: float
    elevation_low: float
    location_city: str | None = None
    location_state: str | None = None
    location_country: str | None = None
    achievement_count: int | None = None
    kudos_count: int | None = None
    comment_count: int | None = None
    athlete_count: int | None = None


class StravaGear(BaseModel):
    id: int
    name: str
    brand: str
    model: str
    type: str
    description: str | None = None
    image: str | None = None
    is_default: bool | None = None