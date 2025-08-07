# Unused Functions and Code Analysis

## Summary
After analyzing the codebase, I've identified several database functions and other code that appear to be unused and can be removed to simplify the codebase.

## Database Functions (`fitness/db/`)

### In `runs.py` - Unused Functions:
1. **`create_run()`** - Not used anywhere, replaced by `upsert_run()` and `bulk_create_runs()`
2. **`get_run_by_id()`** - Not used in the codebase
3. **`get_runs_in_date_range()`** - Not used, replaced by `get_runs_with_shoes_in_date_range()`
4. **`get_runs_by_source()`** - Not used
5. **`soft_delete_runs_by_source()`** - Not used
6. **`delete_runs_by_source()`** - Not used
7. **`soft_delete_run()`** - Not used
8. **`restore_run()`** - Not used
9. **`run_exists()`** - Not used
10. **`upsert_run()`** - Not used, bulk operations are preferred

### In `shoes.py` - Unused Functions:
1. **`create_shoe()`** - Not used, shoes are created via `_ensure_shoe_exists()` in runs.py
2. **`get_shoe_by_name()`** - Not used
3. **`shoe_exists()`** - Not used
4. **`upsert_shoe()`** - Not used
5. **`retire_shoe()`** - Not used (uses `retire_shoe_by_id()` instead)
6. **`unretire_shoe()`** - Not used (uses `unretire_shoe_by_id()` instead)
7. **`soft_delete_shoe()`** - Not used
8. **`restore_shoe()`** - Not used
9. **`delete_shoe()`** - Not used

### In `connection.py` - Unused Functions:
1. **`get_database_url()`** - Only used internally by other connection functions
2. **`get_db_connection()`** - Not used directly, only via `get_db_cursor()`

## API/App Layer

### Services Directory
The entire `fitness/services/` directory appears to be empty except for `__init__.py`, suggesting it's not being used.

### Redundant Code Patterns

1. **Duplicate sorting logic** - `sort_runs()` and `sort_runs_with_shoes()` in app.py have nearly identical implementations
2. **Multiple run retrieval patterns** - The codebase has both `Run` and `RunWithShoes` models with separate database functions

## Recommendations

### 1. Remove Unused Database Functions
Remove all the unused functions listed above from `runs.py` and `shoes.py`. This will significantly reduce the codebase size and maintenance burden.

### 2. Consolidate Connection Functions
In `connection.py`, consider making `get_database_url()` and `get_db_connection()` private (prefix with `_`) since they're only used internally.

### 3. Remove Empty Services Directory
Delete the `fitness/services/` directory if it's not being used.

### 4. Consolidate Sorting Logic
Create a generic sorting function that can handle both `Run` and `RunWithShoes` objects to eliminate code duplication.

### 5. Standardize Run Models
Consider consolidating to use `RunWithShoes` everywhere since shoe information is often needed, eliminating the need for duplicate database functions.

## Functions Currently in Use

### Database Functions Being Used:
- `get_db_cursor()` - Used throughout for database access
- `get_sqlalchemy_database_url()` - Used by Alembic for migrations
- `get_all_runs()` - Used in dependencies
- `get_existing_run_ids()` - Used for checking existing runs
- `bulk_create_runs()` - Used for efficient bulk inserts
- `get_runs_with_shoes()` - Used in API endpoints
- `get_runs_with_shoes_in_date_range()` - Used in API endpoints
- `get_shoes()` - Used in metrics endpoint
- `get_shoe_by_id()` - Used in shoe routes
- `retire_shoe_by_id()` - Used in shoe routes
- `unretire_shoe_by_id()` - Used in shoe routes
- `get_existing_shoes_by_names()` - Used in bulk operations
- `bulk_create_shoes_by_names()` - Used in bulk operations

This analysis shows that approximately 60% of the database functions are unused, presenting a significant opportunity for simplification.