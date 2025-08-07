import os
from dotenv import load_dotenv

# Load env vars before any app code runs.
env = os.getenv("ENV", "dev")
if env not in ("dev", "prod"):
    raise ValueError(f"Invalid environment: {env}")
load_dotenv(f".env.{env}", verbose=True)
