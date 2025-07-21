# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Structure

This is a fitness dashboard application with two main components:
- **API** (`/api`): Python FastAPI backend that serves running data from Strava and MapMyFitness
- **Dashboard** (`/dashboard`): React TypeScript frontend with TailwindCSS and shadcn/ui components

The API loads data from two sources:
1. MapMyFitness: Historical runs downloaded as CSV
2. Strava: Current outdoor runs via API integration

## Development Commands

### API (Python)
- **Start dev server**: `cd api && make dev` (or `uv run -m uvicorn fitness.app:app`)
- **Start production server**: `cd api && make serve`
- **Run tests**: `cd api && make test` (unit tests only)
- **Run integration tests**: `cd api && make int-test` (requires Strava auth)
- **Run all tests**: `cd api && make all-test`
- **Lint**: `cd api && make lint` (uses ruff)
- **Format**: `cd api && make format` (uses ruff)
- **Type check**: `cd api && make ty` (uses ty)
- **General Python Runs**: Remember that you should generally run python with `uv run python`

### Dashboard (React)
- **Start dev server**: `cd dashboard && npm run dev`
- **Build**: `cd dashboard && npm run build`
- **Preview build**: `cd dashboard && npm run preview`
- **Lint**: `cd dashboard && npm run lint`
- **Format**: `cd dashboard && npm run format` (uses prettier)

## Architecture

### API Structure
- `fitness/app/`: FastAPI application with CORS for local development
  - `app.py`: Main FastAPI app with runs endpoint and data refresh
  - `metrics.py`: Router with aggregation endpoints (mileage, training load, etc.)
  - `dependencies.py`: Dependency injection for caching loaded runs data
- `fitness/load/`: Data loading from Strava API and MapMyFitness CSV
  - `strava/`: Strava API client and data loading
  - `mmf/`: MapMyFitness CSV parsing and models
- `fitness/agg/`: Data aggregation functions
  - `mileage.py`: Daily/period mileage calculations
  - `training_load.py`: TRIMP calculation and training stress balance
  - `shoes.py`: Shoe mileage tracking
  - `seconds.py`: Time-based aggregations
- `fitness/models/`: Pydantic models for runs and training load
- Uses dependency injection to cache loaded runs data

### Frontend Structure
- Zustand store (`src/store.ts`) manages global state for date ranges
- React Query (@tanstack/react-query) for API data fetching
- Main components:
  - `AllTimeStatsPanel`: Lifetime running statistics
  - `TimePeriodStatsPanel/`: Time-based analysis with charts
    - `BurdenOverTimeChart`: Training load burden visualization
    - `FreshnessChart`: Training stress balance chart
    - `DailyTrimpChart`: Daily training impulse (TRIMP) chart
    - `DateRangePanel`: Date selection controls
  - `ShoeStatsPanel/`: Shoe mileage tracking and charts
- UI components from shadcn/ui with Radix primitives
- Recharts for data visualization
- TailwindCSS v4 for styling

### Key Data Types
- **Run**: Individual running activity with date, distance, duration, type, source, heart rate, shoes
- **TrainingLoad**: ATL (Acute), CTL (Chronic), TSB (Training Stress Balance)
- **DayTrainingLoad**: Daily training load with TRIMP values
- **DayMileage**: Daily aggregated mileage
- **ShoeMileage**: Total mileage per shoe

### Key Features
- **Training Load Analysis**: TRIMP-based training impulse calculations
- **Training Stress Balance**: Acute (ATL) vs Chronic (CTL) training load with TSB
- **Shoe Tracking**: Mileage accumulation per shoe pair
- **Data Refresh**: Manual refresh endpoint to reload Strava data
- **Date Filtering**: Configurable date ranges for all metrics

### Timezone Handling

**Current Behavior:**
- **Strava Data**: ✅ Properly handles UTC timezones
  - Uses `start_date` field (UTC) from Strava API
  - Token expiration uses UTC time
  - Date conversion: `strava_run.start_date.date()` converts UTC datetime to date
- **MapMyFitness Data**: ✅ Now standardized to UTC
  - CSV dates are converted from local timezone to UTC during loading
  - Configurable via `MMF_TIMEZONE` environment variable (defaults to "America/Chicago")
  - Original date preserved in `workout_date`, UTC date stored in `workout_date_utc`
  - `Run.from_mmf()` uses UTC date for consistency with Strava data
- **Run Model**: Uses timezone-naive `date` type representing UTC dates

**Configuration:**
- Set `MMF_TIMEZONE` environment variable to specify the timezone for MMF data
- Example: `export MMF_TIMEZONE="America/New_York"` for Eastern timezone
- Defaults to "America/Chicago" if not specified

**Benefits:**
- Consistent date assignment across data sources
- Training load calculations use UTC dates uniformly
- Activities near midnight are bucketed consistently

**Note:** Timezone conversion assumes MMF dates represent the start of the day in the specified timezone, then converts to UTC date.

The dashboard displays running metrics including weekly/monthly stats, training load over time (burden/freshness), daily TRIMP charts, and shoe mileage tracking.