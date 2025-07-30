#!/usr/bin/env python3
"""
Script to run database migrations.

This script can be used to:
1. Run pending migrations
2. Check migration status
3. Initialize the database with sample data
"""

import os
import sys
from pathlib import Path

# Add the current directory to the Python path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

from fitness.database import create_tables, get_session_context
from fitness.services.run_service import RunService
from fitness.services.data_sync import DataSyncService
from fitness.load.strava.client import StravaClient


def run_migrations():
    """Run database migrations and setup."""
    print("🏃 Running database migrations...")
    
    # Create tables (this is equivalent to running migrations for now)
    create_tables()
    print("✅ Database tables created successfully!")
    
    return True


def sync_initial_data():
    """Sync initial data from external sources."""
    print("📊 Syncing initial data from external sources...")
    
    try:
        # Create services
        run_service = RunService()
        sync_service = DataSyncService(run_service)
        strava_client = StravaClient.from_env()
        
        # Sync data
        result = sync_service.sync_all_runs_from_sources(strava_client)
        
        print(f"✅ Data sync completed successfully!")
        print(f"   - Cleared {result['cleared_runs']} existing runs")
        print(f"   - Loaded {result['loaded_runs']} runs from external sources")
        print(f"   - Sources: {', '.join(result['sources_synced'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data sync failed: {e}")
        return False


def check_database_connection():
    """Check if database connection works."""
    print("🔌 Checking database connection...")
    
    try:
        with get_session_context() as session:
            # Try a simple query
            session.exec("SELECT 1").first()
        
        print("✅ Database connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("   Make sure your DATABASE_URL environment variable is set correctly.")
        return False


def main():
    """Main migration script."""
    print("🎯 Fitness App Database Setup")
    print("=" * 40)
    
    # Check if DATABASE_URL is set
    if not os.getenv("DATABASE_URL"):
        print("❌ DATABASE_URL environment variable not set!")
        print("   Please set DATABASE_URL to your PostgreSQL connection string.")
        sys.exit(1)
    
    # Check database connection
    if not check_database_connection():
        sys.exit(1)
    
    # Run migrations
    if not run_migrations():
        sys.exit(1)
    
    # Ask if user wants to sync initial data
    if len(sys.argv) > 1 and sys.argv[1] == "--sync-data":
        sync_initial_data()
    else:
        print("\n💡 To sync initial data from external sources, run:")
        print("   python run_migration.py --sync-data")
    
    print("\n🎉 Database setup complete!")
    print("   Your app is now ready to use the PostgreSQL database.")


if __name__ == "__main__":
    main()