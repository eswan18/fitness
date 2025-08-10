#!/usr/bin/env python3
"""
One-time script to get Google OAuth tokens for Calendar API access.
Run this script to get the ACCESS_TOKEN and REFRESH_TOKEN for your .env file.
"""

import os
import sys
from urllib.parse import urlencode
import webbrowser
import urllib.request
import urllib.parse
import json


def get_google_oauth_tokens():
    """Guide user through OAuth flow to get tokens."""

    print("🔐 Google Calendar OAuth Token Setup")
    print("=" * 50)

    # Get credentials from user
    client_id = input("\nEnter your Google Client ID: ").strip()
    if not client_id:
        print("❌ Client ID is required!")
        return False

    client_secret = input("Enter your Google Client Secret: ").strip()
    if not client_secret:
        print("❌ Client Secret is required!")
        return False

    # OAuth 2.0 parameters
    redirect_uri = "urn:ietf:wg:oauth:2.0:oob"  # For desktop apps
    scope = "https://www.googleapis.com/auth/calendar"

    # Step 1: Build authorization URL
    auth_params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "response_type": "code",
        "access_type": "offline",  # This gives us a refresh token
        "prompt": "consent",  # Force consent to get refresh token
    }

    auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(auth_params)}"

    print(f"\n📋 Step 1: Authorize the application")
    print(f"Opening browser to: {auth_url}")
    print(f"\nIf browser doesn't open, copy and paste this URL:")
    print(f"{auth_url}")

    # Open browser
    try:
        webbrowser.open(auth_url)
    except Exception:
        print("Could not open browser automatically")

    # Get authorization code from user
    print(f"\n📋 Step 2: Get authorization code")
    print(f"1. Sign in to your Google account")
    print(f"2. Grant permission to access Google Calendar")
    print(f"3. Copy the authorization code from the browser")

    auth_code = input(f"\nEnter the authorization code: ").strip()
    if not auth_code:
        print("❌ Authorization code is required!")
        return False

    # Step 2: Exchange code for tokens
    print(f"\n📋 Step 3: Exchanging code for tokens...")

    token_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": auth_code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }

    try:
        # Make token request
        token_url = "https://oauth2.googleapis.com/token"
        data = urllib.parse.urlencode(token_data).encode()

        request = urllib.request.Request(token_url, data=data, method="POST")
        request.add_header("Content-Type", "application/x-www-form-urlencoded")

        with urllib.request.urlopen(request) as response:
            result = json.loads(response.read().decode())

        access_token = result.get("access_token")
        refresh_token = result.get("refresh_token")

        if not access_token or not refresh_token:
            print("❌ Failed to get tokens!")
            print(f"Response: {result}")
            return False

        # Success!
        print(f"\n✅ Successfully obtained tokens!")
        print(f"\n📝 Add these to your .env.dev file:")
        print(f"=" * 50)
        print(f"GOOGLE_CLIENT_ID={client_id}")
        print(f"GOOGLE_CLIENT_SECRET={client_secret}")
        print(f"GOOGLE_ACCESS_TOKEN={access_token}")
        print(f"GOOGLE_REFRESH_TOKEN={refresh_token}")
        print(f"=" * 50)

        # Also save to a file for convenience
        with open("google_credentials.txt", "w") as f:
            f.write(f"# Add these to your .env.dev file\n")
            f.write(f"GOOGLE_CLIENT_ID={client_id}\n")
            f.write(f"GOOGLE_CLIENT_SECRET={client_secret}\n")
            f.write(f"GOOGLE_ACCESS_TOKEN={access_token}\n")
            f.write(f"GOOGLE_REFRESH_TOKEN={refresh_token}\n")

        print(f"\n💾 Credentials also saved to 'google_credentials.txt'")
        print(f"\n🎉 Setup complete! You can now use Google Calendar sync.")

        return True

    except Exception as e:
        print(f"❌ Error exchanging code for tokens: {e}")
        return False


if __name__ == "__main__":
    print("This script will help you get Google OAuth tokens for Calendar API access.")
    print("Make sure you have:")
    print("1. ✅ Created a Google Cloud Console project")
    print("2. ✅ Enabled Google Calendar API")
    print("3. ✅ Created OAuth 2.0 Desktop credentials")
    print("4. ✅ Have your Client ID and Client Secret ready")

    proceed = input("\nReady to proceed? (y/N): ").strip().lower()
    if proceed != "y":
        print("Exiting. Run this script when you're ready!")
        sys.exit(0)

    success = get_google_oauth_tokens()
    if success:
        print(
            f"\n🚀 Next step: Add the credentials to your .env.dev file and test the integration!"
        )
    else:
        print(f"\n❌ Setup failed. Please check the steps and try again.")
