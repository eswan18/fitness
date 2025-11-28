#!/usr/bin/env python3
"""
One-time script to create the oauth_credentials table for storing OAuth tokens.
Run this script once to set up the database table.
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables first
env = os.getenv("ENV", "dev")
if env in ("dev", "prod"):
    load_dotenv(f".env.{env}", verbose=True)

# Add parent directory to path so we can import fitness modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fitness.db.connection import get_db_cursor


def create_oauth_credentials_table():
    """Create the oauth_credentials table if it doesn't exist."""

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS oauth_credentials (
        id SERIAL PRIMARY KEY,
        provider VARCHAR(50) NOT NULL UNIQUE,
        client_id TEXT NOT NULL,
        client_secret TEXT NOT NULL,
        access_token TEXT NOT NULL,
        refresh_token TEXT NOT NULL,
        expires_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Create index on provider for fast lookups
    CREATE INDEX IF NOT EXISTS idx_oauth_credentials_provider ON oauth_credentials(provider);

    -- Create trigger to update updated_at timestamp
    CREATE OR REPLACE FUNCTION update_oauth_credentials_updated_at()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS oauth_credentials_updated_at_trigger ON oauth_credentials;
    CREATE TRIGGER oauth_credentials_updated_at_trigger
        BEFORE UPDATE ON oauth_credentials
        FOR EACH ROW
        EXECUTE FUNCTION update_oauth_credentials_updated_at();
    """

    try:
        with get_db_cursor() as cursor:
            cursor.execute(create_table_sql)
            print("✅ Successfully created oauth_credentials table")

            # Verify table was created
            cursor.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = 'oauth_credentials'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()

            print("\n📋 Table schema:")
            for col_name, col_type in columns:
                print(f"  - {col_name}: {col_type}")

            print("\n🎉 Table creation complete!")
            print(
                "\nNext step: Run 'python scripts/migrate_google_tokens_to_db.py' to migrate your existing tokens"
            )

            return True

    except Exception as e:
        print(f"❌ Error creating table: {e}")
        return False


if __name__ == "__main__":
    print("Creating oauth_credentials table...")
    print("=" * 50)

    # Check if DATABASE_URL is set
    if not os.getenv("DATABASE_URL"):
        print("❌ DATABASE_URL environment variable is not set!")
        print("Please set DATABASE_URL in your .env file")
        sys.exit(1)

    success = create_oauth_credentials_table()
    sys.exit(0 if success else 1)
