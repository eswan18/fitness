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
- `id`: Primary key (string) - deterministic ID based on source
- `datetime_utc`: When the run occurred (UTC)
- `type`: Run type ('Outdoor Run' or 'Treadmill Run')
- `distance`: Distance in miles
- `duration`: Duration in seconds
- `source`: Data source ('MapMyFitness' or 'Strava')
- `avg_heart_rate`: Average heart rate (optional)
- `shoes`: Shoe name (optional)
- `created_at`: Record creation timestamp
- `updated_at`: Record update timestamp

And the `shoes` table with the following structure:
- `id`: Primary key (string) - normalized from shoe name
- `name`: Display name of the shoe (unique)
- `retired`: Boolean indicating if shoe is retired
- `retirement_date`: Date when shoe was retired (optional)
- `notes`: Retirement notes (optional)
- `created_at`: Record creation timestamp
- `updated_at`: Record update timestamp

## Run ID System

The application uses deterministic IDs to ensure data consistency:

### Strava Runs
- Use Strava's native activity ID with prefix: `strava_{activity_id}`
- Example: `strava_1234567890`

### MapMyFitness Runs  
- Extract workout ID directly from the activity link URL
- Link format: `https://www.mapmyfitness.com/workout/{workout_id}`
- ID format: `mmf_{workout_id}`
- Example: `mmf_8622076198`

### Shoes
- Generate deterministic ID from shoe name normalization:
  - Convert to lowercase
  - Replace spaces and special characters with underscores  
  - Remove consecutive underscores
  - Strip leading/trailing underscores
- Examples:
  - "Nike Air Zoom Pegasus 38" → `nike_air_zoom_pegasus_38`
  - "Brooks Ghost 15" → `brooks_ghost_15`
  - "New Balance M1080K10" → `new_balance_m1080k10`

This approach ensures:
- **Idempotent operations**: Re-importing the same data won't create duplicates
- **Data integrity**: IDs remain consistent across imports
- **Update safety**: Changes to existing runs are handled gracefully

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

# Get specific run by ID
run = get_run_by_id("strava_1234567890")

# Get runs in date range
runs = get_runs_in_date_range(start_date, end_date)

# Create a new run
run_id = create_run(run_object)

# Insert or update (recommended for imports)
run_id = upsert_run(run_object)

# Bulk operations
count = bulk_create_runs(list_of_runs)
count = bulk_upsert_runs(list_of_runs)  # Handles updates gracefully

# Check if run exists
exists = run_exists(run_object)

# Shoes operations
from fitness.db.shoes import *

# Get all shoes
shoes = get_all_shoes()

# Get specific shoe by name or ID
shoe = get_shoe_by_name("Nike Air Zoom Pegasus 38")
shoe = get_shoe_by_id("nike_air_zoom_pegasus_38")

# Get shoes by status
active_shoes = get_active_shoes()
retired_shoes = get_retired_shoes()

# Create or update shoes
shoe_id = create_shoe(shoe_object)
shoe_id = upsert_shoe(shoe_object)  # Handles updates gracefully

# Retirement management
retire_shoe("Nike Air Zoom Pegasus 38", retirement_date, "Worn out after 500 miles")
unretire_shoe("Nike Air Zoom Pegasus 38")

# Check if shoe exists
exists = shoe_exists("Nike Air Zoom Pegasus 38")
```

### Refreshing Data

The API includes functionality to refresh data from external sources:

```python
# This will re-fetch from Strava and MMF, then upsert to the database
# Uses deterministic IDs to handle updates without duplicates
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
- **Deterministic IDs**: Ensures data consistency and enables safe upsert operations 