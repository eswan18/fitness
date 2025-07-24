"""Service for managing shoe retirement status."""

import json
from datetime import date
from pathlib import Path
from typing import Dict, Optional

from pydantic import BaseModel


class ShoeRetirementInfo(BaseModel):
    """Information about a retired shoe."""

    retirement_date: date
    notes: Optional[str] = None


class RetirementService:
    """Service for managing shoe retirement status."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the retirement service.

        Args:
            config_path: Path to the retirement config file. If None, uses default repo location.
        """
        if config_path is None:
            # Use version-controlled location in the repo's data directory
            repo_root = Path(__file__).parent.parent.parent  # Navigate to api/ root
            data_dir = repo_root / "data"
            data_dir.mkdir(exist_ok=True)
            config_path = data_dir / "retired-shoes.json"
        self.config_path = config_path

    def _load_retired_shoes(self) -> Dict[str, ShoeRetirementInfo]:
        """Load retired shoes from the JSON file."""
        if not self.config_path.exists():
            return {}

        try:
            with open(self.config_path, "r") as f:
                data = json.load(f)

            # Convert dict to ShoeRetirementInfo objects
            retired_shoes = {}
            for shoe_name, info in data.items():
                retired_shoes[shoe_name] = ShoeRetirementInfo(
                    retirement_date=date.fromisoformat(info["retirement_date"]),
                    notes=info.get("notes"),
                )
            return retired_shoes
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # If file is corrupted, log warning and return empty dict
            print(f"Warning: Could not load retired shoes from {self.config_path}: {e}")
            return {}

    def _save_retired_shoes(self, retired_shoes: Dict[str, ShoeRetirementInfo]) -> None:
        """Save retired shoes to the JSON file."""
        # Convert ShoeRetirementInfo objects to dict
        data = {}
        for shoe_name, info in retired_shoes.items():
            data[shoe_name] = {
                "retirement_date": info.retirement_date.isoformat(),
                "notes": info.notes,
            }

        # Ensure directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_path, "w") as f:
            json.dump(data, f, indent=2)

    def is_shoe_retired(self, shoe_name: str) -> bool:
        """Check if a shoe is retired."""
        retired_shoes = self._load_retired_shoes()
        return shoe_name in retired_shoes

    def get_retirement_info(self, shoe_name: str) -> Optional[ShoeRetirementInfo]:
        """Get retirement information for a shoe."""
        retired_shoes = self._load_retired_shoes()
        return retired_shoes.get(shoe_name)

    def retire_shoe(
        self, shoe_name: str, retirement_date: date, notes: Optional[str] = None
    ) -> None:
        """Retire a shoe."""
        retired_shoes = self._load_retired_shoes()
        retired_shoes[shoe_name] = ShoeRetirementInfo(
            retirement_date=retirement_date, notes=notes
        )
        self._save_retired_shoes(retired_shoes)

    def unretire_shoe(self, shoe_name: str) -> bool:
        """Unretire a shoe. Returns True if shoe was retired, False if it wasn't."""
        retired_shoes = self._load_retired_shoes()
        if shoe_name in retired_shoes:
            del retired_shoes[shoe_name]
            self._save_retired_shoes(retired_shoes)
            return True
        return False

    def list_retired_shoes(self) -> Dict[str, ShoeRetirementInfo]:
        """List all retired shoes with their retirement information."""
        return self._load_retired_shoes()
