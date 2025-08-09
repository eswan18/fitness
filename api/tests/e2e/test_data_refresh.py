"""End-to-end tests for data refresh functionality.

Note: These tests are currently skipped to avoid hitting external APIs during testing.
The /update-data endpoint requires Strava authentication which would interrupt test runs.
"""

import pytest
from datetime import datetime
from fitness.models import Run
from fitness.db.runs import bulk_create_runs, get_all_runs


@pytest.mark.skip(reason="Skipping data refresh tests to avoid external API calls")
@pytest.mark.e2e
def test_update_data_endpoint_method_not_allowed(client):
    """Test that /update-data only accepts POST requests."""
    # Test that endpoint rejects GET method
    res = client.get("/update-data")
    assert res.status_code == 405  # Method not allowed