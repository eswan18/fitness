# Fitness API – Setup & Usage

## Overview

This API provides analysis and aggregation of your running data from two sources:
- **MapMyFitness**: Historical and treadmill runs (CSV export)
- **Strava**: Outdoor runs (via Strava API)

---

## 1. Prerequisites
- Python 3.13+ (recommended: [uv](https://github.com/astral-sh/uv))
- [Make](https://www.gnu.org/software/make/) (for convenience commands)
- Strava account (for outdoor run data)
- MapMyFitness CSV export (for historical/treadmill runs)

---

## 2. Environment Variables

Create a `.env` file in the `api/` directory with the following variables:

```env
# Required for Strava API integration
STRAVA_CLIENT_ID=your_strava_client_id
STRAVA_CLIENT_SECRET=your_strava_client_secret
STRAVA_REFRESH_TOKEN=your_strava_refresh_token

# Required for MapMyFitness data
MMF_DATAFILE=/absolute/path/to/your/mapmyfitness.csv

# Optional: Set the timezone for MMF data (default: America/Chicago)
MMF_TIMEZONE=America/Chicago

# Optional: Google Calendar sync (leave blank to disable sync features)
GOOGLE_CLIENT_ID=your_google_oauth_client_id
GOOGLE_CLIENT_SECRET=your_google_oauth_client_secret
GOOGLE_ACCESS_TOKEN=your_google_access_token
GOOGLE_REFRESH_TOKEN=your_google_refresh_token
# Optional: target calendar (defaults to "primary" if unset)
GOOGLE_CALENDAR_ID=your_calendar_id
```

- **STRAVA_CLIENT_ID / SECRET / REFRESH_TOKEN**:  
  Get these from your Strava API application settings. See "Strava Setup" section below for initial setup.
- **STRAVA_ACCESS_TOKEN / EXPIRES_AT** (optional):  
  Auto-managed by the system after initial setup. These are automatically refreshed and updated.
- **MMF_DATAFILE**:  
  Path to your MapMyFitness CSV export (see below).
- **MMF_TIMEZONE**:  
  The timezone your MMF data was recorded in. Defaults to "America/Chicago" if not set.
- **GOOGLE_CLIENT_ID / SECRET**:  
  OAuth 2.0 credentials from Google Cloud Console (https://console.cloud.google.com). Required for Google Calendar sync.
- **GOOGLE_ACCESS_TOKEN / REFRESH_TOKEN**:  
  OAuth tokens for your Google account. See "Google Calendar Setup" section below for initial setup.
- **GOOGLE_CALENDAR_ID** (optional):
  Calendar to create events in. If not provided, the API will use the `primary` calendar.

---

## 3. Strava Setup

Strava integration is required for fetching running activities. This section covers the complete setup and ongoing maintenance of OAuth tokens.

### Initial Setup

1. **Create Strava API Application**:
   - Go to [Strava API Settings](https://www.strava.com/settings/api)
   - Click "Create App" and fill in the application details
   - Set "Authorization Callback Domain" to `localhost`
   - Note your Client ID and Client Secret

2. **Get OAuth Tokens**:
   ```sh
   # Run the provided helper script
   python scripts/get_strava_tokens.py
   ```
   
   This script will:
   - Open your browser to Strava's authorization page
   - Handle the OAuth callback automatically
   - Generate all required tokens
   - Save credentials to `strava_credentials.txt`

3. **Add to Environment File**:
   Copy the generated values to your `.env` file:
   ```sh
   STRAVA_CLIENT_ID=your_client_id
   STRAVA_CLIENT_SECRET=your_client_secret
   STRAVA_ACCESS_TOKEN=your_access_token
   STRAVA_REFRESH_TOKEN=your_refresh_token
   STRAVA_EXPIRES_AT=timestamp
   ```

### Token Management

The system automatically handles token refresh during runtime:
- **Access tokens** expire every 6 hours and are auto-refreshed in memory
- **Refresh tokens** are long-lived and updated in memory when rotated
- **No re-authentication** needed during API session
- **Manual refresh**: Re-run the setup script if tokens become invalid

---

## 4. Google Calendar Setup (Optional)

Google Calendar sync allows you to automatically create calendar events for your runs. This section covers the complete setup and ongoing maintenance of OAuth tokens.

### Initial Setup

1. **Create Google Cloud Console Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select existing one
   - Enable the Google Calendar API
   - Create OAuth 2.0 Desktop Application credentials
   - Download the credentials (you'll need Client ID and Client Secret)

2. **Get OAuth Tokens**:
   ```sh
   # Run the provided helper script
   python scripts/get_google_tokens.py
   ```
   
   This script will:
   - Guide you through the OAuth consent flow
   - Open your browser for Google account authorization
   - Exchange the authorization code for access and refresh tokens
   - Save credentials to `google_credentials.txt`

3. **Add Credentials to Environment**:
   ```env
   GOOGLE_CLIENT_ID=your_client_id
   GOOGLE_CLIENT_SECRET=your_client_secret  
   GOOGLE_ACCESS_TOKEN=your_access_token
   GOOGLE_REFRESH_TOKEN=your_refresh_token
   ```

### OAuth Token Lifecycle

**🔄 Automatic Token Management**: The application handles token refresh automatically! You generally **do not** need to re-run the setup script.

- **Access Token**: Expires after ~1 hour, automatically refreshed using refresh token
- **Refresh Token**: Long-lived (typically 6 months to indefinite), stored in your environment variables
- **Auto-Refresh**: When API calls receive 401 (unauthorized), the client automatically refreshes the access token and retries

### When You Need to Re-authenticate

You'll need to re-run `python get_google_tokens.py` only if:

1. **Refresh Token Expires**: 
   - Google revokes refresh tokens after 6+ months of inactivity
   - You'll see persistent 401 errors that don't auto-resolve
   
2. **Credentials Revoked**: 
   - You manually revoke access in Google Account settings
   - Security incident or suspicious activity detected by Google
   
3. **Scope Changes**: 
   - Application requires additional Google API permissions
   - Current implementation only needs `https://www.googleapis.com/auth/calendar`

### Troubleshooting OAuth Issues

**Symptoms of expired/invalid tokens**:
- Sync operations fail with "authentication failed" messages
- API logs show repeated 401 errors that don't resolve
- Google Calendar events not being created

**How to check token status**:
```sh
# Test a sync operation - if it works, tokens are valid
curl -X POST "http://localhost:8000/sync/runs/your_run_id"

# Check failed syncs for authentication errors
curl "http://localhost:8000/sync/runs/failed"
```

**To refresh credentials**:
1. Delete old tokens from `.env` file
2. Re-run: `python get_google_tokens.py`
3. Update `.env` file with new tokens
4. Restart the API server

### Security Notes

- **Never commit OAuth tokens to version control**
- **Refresh tokens are equivalent to passwords** - store securely
- **Access tokens expire quickly** - safe to log for debugging
- **Consider token rotation** if credentials may have been compromised

---

## 4. Getting the Data

### MapMyFitness
- Download your data as CSV from:  
  https://www.mapmyfitness.com/workout/export/csv
- Save the file and set `MMF_DATAFILE` to its path.

### Strava
- The API will prompt you to authorize the app on first run if credentials are missing or expired.

---

## 5. Installing Dependencies

From the `api/` directory:

```sh
uv sync
```

This will install all dependencies as specified in the `uv.lock` file, ensuring a reproducible environment.

---

## 6. Starting the API Server

- **Development server (with auto-reload):**
  ```sh
  ENV=dev make dev
  # or
  ENV=dev uv run -m uvicorn fitness.app.app:app --reload
  ```

- **Production server:**
  ```sh
  ENV=prod make serve
  # or
  ENV=prod uv run -m uvicorn fitness.app.app:app
  ```

- The API will be available at `http://localhost:8000`.

- You can optionally also set the log level with the `LOG_LEVEL` environment variable. For example:
  ```sh
  ENV=dev LOG_LEVEL=debug make dev
  ```

---

## 7. API Documentation

- Interactive API docs (auto-generated by FastAPI) are available at:  
  `http://localhost:8000/docs`

---

## 8. Key Endpoints

- `GET /runs` — All runs with optional date filtering, timezone-aware filtering, and sorting.
- `GET /runs/details` — Detailed runs including shoes, shoe retirement notes, run version, and Google Calendar sync info. Optional query: `synced=true|false` to filter by Google Calendar sync status. Alias: `/runs-details`.
- `PATCH /runs/{run_id}` — Edit a run (with history tracking).
- `GET /metrics/...` — Aggregated metrics (see docs for full list).
- `POST /sync/runs/{run_id}` — Sync a run to Google Calendar; `DELETE` to remove.

## 9. Example: Quick Test

Fetch all runs:
```sh
curl "http://localhost:8000/runs"
```

Fetch metrics (see `/docs` for all endpoints):
```sh
curl "http://localhost:8000/metrics/mileage/by-shoe"
```

Fetch detailed runs (includes shoes, run version, and Google Calendar sync status):
```sh
curl "http://localhost:8000/runs/details?start=2024-01-01&end=2024-12-31&sort_by=distance&sort_order=desc&synced=true"
```

Response fields (per run):
- `id`, `datetime_utc`, `type`, `distance`, `duration`, `source`, `avg_heart_rate`
- `shoe_id`, `shoes`, `shoe_retirement_notes`, `deleted_at`, `version`
- `is_synced`, `sync_status`, `synced_at`, `google_event_id`, `synced_version`, `error_message`

Test Google Calendar sync (if configured):
```sh
# Sync a run to Google Calendar
curl -X POST "http://localhost:8000/sync/runs/your_run_id"

# Check sync status
curl "http://localhost:8000/sync/runs/your_run_id/status"

# Remove sync from Google Calendar  
curl -X DELETE "http://localhost:8000/sync/runs/your_run_id"
```

---

## 10. Testing

Before running tests, install dev dependencies (pytest, testcontainers, etc.):

```sh
uv sync --group dev
```

- **Unit tests only** (fast, no external services, no containers):
  ```sh
  make test
  ```

- **End-to-end (E2E) API + DB workflow tests** (uses Testcontainers Postgres + Alembic):
  - Requires Docker running
  ```sh
  make e2e-test
  ```

- **Integration tests with Strava (external system)**:
  - Requires valid Strava credentials in `.env.dev`
  ```sh
  make int-test
  ```

- **All tests**:
  ```sh
  make all-test
  ```

- **Linting, formatting, and type checks**:
  ```sh
  make lint
  make format
  make ty
  ```
