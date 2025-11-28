"""Load environment variables early for the FastAPI app.

Selects the .env file based on ENV ("dev" or "prod") before any other imports
run, so dependent modules see configured settings.
"""

import os
from typing import Literal, cast
from dotenv import load_dotenv

EnvironmentName = Literal[
    "dev", "prod", "vercel-production", "vercel-preview", "vercel-development"
]
VercelEnvironmentName = Literal["production", "preview", "development"]

# Load env vars before any app code runs.
if "VERCEL_ENV" in os.environ:
    # We're running on vercel and don't need to load the env file.
    pass
elif (env := os.getenv("ENV", "dev")) in ("dev", "prod"):
    print(f"Loading environment variables from .env.{env}")
    load_dotenv(f".env.{env}", verbose=True)
else:
    raise ValueError("Invalid environment and VERCEL_ENV is not set")


def get_current_environment() -> EnvironmentName:
    """Get the current environment (dev, prod, or vercel)."""
    if "VERCEL_ENV" in os.environ:
        vercel_env: VercelEnvironmentName = os.environ["VERCEL_ENV"].lower()
        return f"vercel-{vercel_env}"
    env = os.getenv("ENV", "dev")
    if env not in ("dev", "prod"):
        raise ValueError(f"Invalid environment: {env}")
    return cast(Literal["dev", "prod"], env)
