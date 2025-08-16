#!/usr/bin/env python3
"""
One-time script to get Strava OAuth tokens for API access.
Run this script to get the ACCESS_TOKEN and REFRESH_TOKEN for your .env file.
"""

import sys
import socket
import http.server
from urllib.parse import urlparse, parse_qs, urlencode
import webbrowser
import urllib.request
import urllib.parse
import json


def find_open_port() -> int:
    """Find an open port to use for the redirect URI."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def receive_code(port: int) -> str:
    """Receive authorization code from OAuth callback."""
    code = None

    class OAuthCallbackHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self) -> None:
            # Extract the query parameters
            query_components = parse_qs(urlparse(self.path).query)
            nonlocal code
            code_list = query_components.get("code")
            if code_list:
                code = code_list[0]

            # Send response
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            success_html = """
            <html>
            <head><title>Strava Authorization</title></head>
            <body style="font-family: Arial, sans-serif; text-align: center; margin-top: 50px;">
                <h2>✅ Authorization Successful!</h2>
                <p>You can close this window and return to the terminal.</p>
            </body>
            </html>
            """
            self.wfile.write(success_html.encode())

        def log_message(self, format, *args):
            # Suppress HTTP server logs
            pass

    server = http.server.HTTPServer(("localhost", port), OAuthCallbackHandler)
    print(f"🌐 Starting local server on http://localhost:{port}")
    print("   Waiting for authorization callback...")

    # Handle just one request, then shut down
    server.handle_request()

    if code is not None:
        return code
    else:
        raise ValueError("No authorization code received.")


def get_strava_oauth_tokens():
    """Guide user through OAuth flow to get tokens."""

    print("🔐 Strava OAuth Token Setup")
    print("=" * 50)

    # Get credentials from user
    client_id = input("\nEnter your Strava Client ID: ").strip()
    if not client_id:
        print("❌ Client ID is required!")
        return False

    client_secret = input("Enter your Strava Client Secret: ").strip()
    if not client_secret:
        print("❌ Client Secret is required!")
        return False

    # Find available port for redirect
    port = find_open_port()
    redirect_uri = f"http://localhost:{port}/"

    # OAuth 2.0 parameters
    auth_params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "activity:read_all",
        "approval_prompt": "auto",
    }

    auth_url = f"https://www.strava.com/oauth/authorize?{urlencode(auth_params)}"

    print("\n📋 Step 1: Authorize the application")
    print("This will open your browser to Strava's authorization page.")
    print("If browser doesn't open automatically, copy and paste this URL:")
    print(f"{auth_url}")

    # Open browser
    try:
        webbrowser.open(auth_url)
    except Exception:
        print("Could not open browser automatically")

    # Get authorization code via local server
    print("\n📋 Step 2: Waiting for authorization...")
    print("1. Sign in to your Strava account in the browser")
    print("2. Click 'Authorize' to grant permission")
    print("3. You'll be redirected back automatically")

    try:
        auth_code = receive_code(port)
        print(f"✅ Received authorization code: {auth_code[:10]}...")
    except Exception as e:
        print(f"❌ Failed to receive authorization code: {e}")
        return False

    # Step 3: Exchange code for tokens
    print("\n📋 Step 3: Exchanging code for tokens...")

    token_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": auth_code,
        "grant_type": "authorization_code",
    }

    try:
        # Make token request
        token_url = "https://www.strava.com/oauth/token"
        data = urllib.parse.urlencode(token_data).encode()

        request = urllib.request.Request(token_url, data=data, method="POST")
        request.add_header("Content-Type", "application/x-www-form-urlencoded")

        with urllib.request.urlopen(request) as response:
            result = json.loads(response.read().decode())

        access_token = result.get("access_token")
        refresh_token = result.get("refresh_token")
        expires_at = result.get("expires_at")
        expires_in = result.get("expires_in")

        if not access_token or not refresh_token:
            print("❌ Failed to get tokens!")
            print(f"Response: {result}")
            return False

        # Success!
        print("\n✅ Successfully obtained tokens!")
        print(f"   Access token expires at: {expires_at} (in {expires_in} seconds)")
        print("\n📝 Add these to your .env file:")
        print("=" * 50)
        print(f"STRAVA_CLIENT_ID={client_id}")
        print(f"STRAVA_CLIENT_SECRET={client_secret}")
        print(f"STRAVA_ACCESS_TOKEN={access_token}")
        print(f"STRAVA_REFRESH_TOKEN={refresh_token}")
        print(f"STRAVA_EXPIRES_AT={expires_at}")
        print("=" * 50)

        # Also save to a file for convenience
        with open("strava_credentials.txt", "w") as f:
            f.write("# Add these to your .env file\n")
            f.write(f"STRAVA_CLIENT_ID={client_id}\n")
            f.write(f"STRAVA_CLIENT_SECRET={client_secret}\n")
            f.write(f"STRAVA_ACCESS_TOKEN={access_token}\n")
            f.write(f"STRAVA_REFRESH_TOKEN={refresh_token}\n")
            f.write(f"STRAVA_EXPIRES_AT={expires_at}\n")

        print("\n💾 Credentials also saved to 'strava_credentials.txt'")
        print(
            "\n🎉 Setup complete! You can now sync Strava data without re-authentication."
        )

        return True

    except Exception as e:
        print(f"❌ Error exchanging code for tokens: {e}")
        return False


if __name__ == "__main__":
    print("This script will help you get Strava OAuth tokens for API access.")
    print("Make sure you have:")
    print(
        "1. ✅ Created a Strava API application at https://www.strava.com/settings/api"
    )
    print("2. ✅ Have your Client ID and Client Secret ready")
    print(
        "3. ✅ Set Authorization Callback Domain to 'localhost' in your Strava app settings"
    )

    proceed = input("\nReady to proceed? (y/N): ").strip().lower()
    if proceed != "y":
        print("Exiting. Run this script when you're ready!")
        sys.exit(0)

    success = get_strava_oauth_tokens()
    if success:
        print(
            "\n🚀 Next step: Add the credentials to your .env file and restart your API!"
        )
        print("   The system will now automatically refresh tokens as needed.")
    else:
        print("\n❌ Setup failed. Please check the steps and try again.")
