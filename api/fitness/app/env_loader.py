"""Load environment variables early for the FastAPI app.

Selects the .env file based on ENV ("dev" or "prod") before any other imports
run, so dependent modules see configured settings.
"""

import os
from dotenv import load_dotenv

# Load env vars before any app code runs.
env = os.getenv("ENV", "dev")
if env not in ("dev", "prod"):
    raise ValueError(f"Invalid environment: {env}")
load_dotenv(f".env.{env}", verbose=True)


def get_current_environment() -> str:
    """Get the current environment (dev or prod)."""
    return os.getenv("ENV", "dev")
