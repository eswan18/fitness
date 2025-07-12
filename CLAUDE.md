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
- **Run tests**: `cd api && make test` (unit tests only)
- **Run integration tests**: `cd api && make int-test` (requires Strava auth)
- **Run all tests**: `cd api && make all-test`
- **Lint**: `cd api && make lint` (uses ruff)
- **Format**: `cd api && make format` (uses ruff)
- **Type check**: `cd api && make ty` (uses ty)

### Dashboard (React)
- **Start dev server**: `cd dashboard && npm run dev`
- **Build**: `cd dashboard && npm run build`
- **Lint**: `cd dashboard && npm run lint`
- **Format**: `cd dashboard && npm run format` (uses prettier)

## Architecture

### API Structure
- `fitness/app/`: FastAPI application with CORS for local development
- `fitness/load/`: Data loading from Strava API and MapMyFitness CSV
- `fitness/agg/`: Data aggregation functions (mileage, training load, shoes)
- `fitness/models/`: Pydantic models for runs and training load
- Uses dependency injection to cache loaded runs data

### Frontend Structure
- Zustand store (`src/store.ts`) manages global state for date ranges
- React Query for API data fetching
- Three main panels: AllTimeStats, TimePeriodStats, ShoesStats
- UI components from shadcn/ui with Radix primitives
- Recharts for data visualization

### Key Data Types
- **Run**: Individual running activity with date, distance, duration, type, source, heart rate, shoes
- **TrainingLoad**: ATL (Acute), CTL (Chronic), TSB (Training Stress Balance)
- **DayMileage**: Daily aggregated mileage
- **ShoeMileage**: Total mileage per shoe

The dashboard displays running metrics including weekly/monthly stats, training load over time (burden/freshness), and shoe mileage tracking.