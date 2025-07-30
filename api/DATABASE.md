# Database Setup Guide

This application has been migrated from in-memory storage to PostgreSQL for persistent data storage.

## Prerequisites

1. **PostgreSQL Database**: You need a running PostgreSQL instance
2. **Environment Variables**: Set up your `DATABASE_URL` environment variable

## Environment Setup

Add the following to your `.env` file in the `api/` directory:

```env
# Database connection
DATABASE_URL=postgresql://username:password@localhost:5432/fitness_db

# Existing variables (Strava, MMF, etc.)
# ... your other environment variables ...
```

### Database URL Format

The `DATABASE_URL` should follow this format:
```
postgresql://[username[:password]@][host[:port]][/database]
```

Examples:
- Local development: `postgresql://postgres:password@localhost:5432/fitness_db`
- With connection parameters: `postgresql://user:pass@localhost:5432/fitness_db?sslmode=require`

## Database Migration

### 1. Install Dependencies

```bash
cd api
uv sync
```

### 2. Create Database

Create your PostgreSQL database (this step depends on your PostgreSQL setup):

```sql
CREATE DATABASE fitness_db;
```

### 3. Run Migrations

Apply the database schema:

```bash
cd api
alembic upgrade head
```

This creates the `runs` table with the following structure:
- `id`: Primary key (auto-increment)
- `datetime_utc`: When the run occurred (UTC)
- `type`: Run type ('Outdoor Run' or 'Treadmill Run')
- `distance`: Distance in miles
- `duration`: Duration in seconds
- `source`: Data source ('MapMyFitness' or 'Strava')
- `avg_heart_rate`: Average heart rate (optional)
- `shoes`: Shoe name (optional)
- `created_at`: Record creation timestamp
- `updated_at`: Record update timestamp

## Database Operations

### Raw SQL Access

The application uses raw SQL queries via psycopg3. Key modules:

- `fitness/db/connection.py`: Database connection management
- `fitness/db/runs.py`: Run-specific database operations

### Available Operations

```python
from fitness.db.runs import *

# Get all runs
runs = get_all_runs()

# Get runs in date range
runs = get_runs_in_date_range(start_date, end_date)

# Create a new run
run_id = create_run(run_object)

# Bulk insert
count = bulk_create_runs(list_of_runs)

# Check if run exists
exists = run_exists(run_object)
```

### Refreshing Data

The API includes functionality to refresh data from external sources:

```python
# This will re-fetch from Strava and MMF, then update the database
fresh_runs = refresh_runs_data()
```

## Creating New Migrations

When you need to modify the database schema:

```bash
cd api
alembic revision -m "Description of your change"
```

Edit the generated migration file in `alembic/versions/`, then apply it:

```bash
alembic upgrade head
```

## Troubleshooting

### Connection Issues

1. **Check DATABASE_URL**: Ensure the format is correct and the database exists
2. **Database permissions**: Make sure your user has CREATE/INSERT/SELECT permissions
3. **Network connectivity**: Verify you can connect to the PostgreSQL server

### Migration Issues

1. **Check dependencies**: Run `uv sync` to ensure all packages are installed
2. **Check database exists**: The database must exist before running migrations
3. **Check credentials**: Ensure your DATABASE_URL credentials are correct

## Architecture Notes

- **No ORM**: Uses raw SQL with psycopg3 for direct database access
- **Connection management**: Uses context managers for automatic connection cleanup
- **Migrations**: Alembic handles schema versioning and migrations
- **Performance**: Includes database indexes on commonly queried fields 