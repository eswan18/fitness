from typing import Literal

from pydantic import BaseModel, TypeAdapter, AwareDatetime

class ActivityAthlete(BaseModel):
    id: int
    resource_state: int

ActivityType = Literal['Workout', 'Ride', 'Walk', 'Run', 'Yoga', 'WeightTraining', 'Hike']

class StravaActivity(BaseModel):
    id: int
    name: str
    resource_state: int
    type: ActivityType
    commute: bool
    start_date: AwareDatetime
    start_date_local: AwareDatetime
    timezone: str
    utc_offset: float
    distance: float
    moving_time: int
    elapsed_time: int
    total_elevation_gain: float
    has_kudoed: bool
    has_heartrate: bool
    athlete: ActivityAthlete
    manual: bool
    kilojoules: float | None = None
    start_latlng: list[float]
    end_latlng: list[float]
    achievement_count: int
    kudos_count: int
    comment_count: int
    athlete_count: int
    total_photo_count: int
    max_speed: float
    from_accepted_tag: bool
    sport_type: str
    trainer: bool
    photo_count: int
    private: bool
    pr_count: int
    heartrate_opt_out: bool
    average_speed: float
    visibility: str
    upload_id: int | None = None
    external_id: str | None = None
    device_watts: bool | None = None
    suffer_score: float | None = None
    workout_type: int | None = None
    gear_id: str | None = None
    elev_low: float | None = None
    elev_high: float | None = None
    max_heartrate: float | None = None
    average_heartrate: float | None = None
    upload_id_str: str | None = None
    average_watts: float | None = None


activity_list_adapter = TypeAdapter(list[StravaActivity])

class StravaGear(BaseModel):
    id: str
    name: str
    nickname: str
    brand_name: str
    model_name: str
    converted_distance: float
    distance: int | float
    notification_distance: int
    primary: bool
    resource_state: int
    retired: bool

gear_list_adapter = TypeAdapter(list[StravaGear])