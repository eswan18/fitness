from fitness.integrations.strava.auth import build_oauth_authorize_url


def test_build_oauth_authorize_url():
    url = build_oauth_authorize_url("https://example.com")
    assert (
        url
        == "https://www.strava.com/oauth/authorize?client_id=test_client_id&redirect_uri=https%3A%2F%2Fexample.com&scope=activity%3Aread_all&response_type=code"
    )
