"""Database models using SQLModel for the fitness app."""

from datetime import datetime
from typing import Literal, TYPE_CHECKING

from sqlmodel import SQLModel, Field, create_engine, Session
from pydantic import ConfigDict

if TYPE_CHECKING:
    pass

# Re-export the existing types for consistency
RunType = Literal["Outdoor Run", "Treadmill Run"]
RunSource = Literal["MapMyFitness", "Strava"]


class RunTable(SQLModel, table=True):
    """Database model for runs table."""
    
    __tablename__ = "runs"
    
    id: int | None = Field(default=None, primary_key=True)
    datetime_utc: datetime = Field(index=True)
    type: RunType
    distance: float = Field(description="Distance in miles")
    duration: float = Field(description="Duration in seconds") 
    source: RunSource = Field(index=True)
    avg_heart_rate: float | None = Field(default=None)
    shoes: str | None = Field(default=None, index=True)
    
    # Timestamps for tracking
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    model_config = ConfigDict(
        # Allow SQLModel to work with SQLAlchemy
        from_attributes=True,
    )


class RunCreate(SQLModel):
    """Model for creating a new run (no id, timestamps auto-generated)."""
    datetime_utc: datetime
    type: RunType
    distance: float
    duration: float
    source: RunSource
    avg_heart_rate: float | None = None
    shoes: str | None = None


class RunRead(SQLModel):
    """Model for reading a run (includes all fields including id and timestamps)."""
    id: int
    datetime_utc: datetime
    type: RunType
    distance: float
    duration: float
    source: RunSource
    avg_heart_rate: float | None = None
    shoes: str | None = None
    created_at: datetime
    updated_at: datetime


class RunUpdate(SQLModel):
    """Model for updating a run (all fields optional)."""
    datetime_utc: datetime | None = None
    type: RunType | None = None
    distance: float | None = None
    duration: float | None = None
    source: RunSource | None = None
    avg_heart_rate: float | None = None
    shoes: str | None = None