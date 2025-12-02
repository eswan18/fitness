#!/usr/bin/env python3
"""
One-time script to get Google OAuth tokens for Calendar API access.
Run this script to get the ACCESS_TOKEN and REFRESH_TOKEN and optionally store them in the database.
"""

import sys
from datetime import datetime, timedelta, timezone
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

    print("\n📋 Step 1: Authorize the application")
    print(f"Opening browser to: {auth_url}")
    print("\nIf browser doesn't open, copy and paste this URL:")
    print(f"{auth_url}")

    # Open browser
    try:
        webbrowser.open(auth_url)
    except Exception:
        print("Could not open browser automatically")

    # Get authorization code from user
    print("\n📋 Step 2: Get authorization code")
    print("1. Sign in to your Google account")
    print("2. Grant permission to access Google Calendar")
    print("3. Copy the authorization code from the browser")

    auth_code = input("\nEnter the authorization code: ").strip()
    if not auth_code:
        print("❌ Authorization code is required!")
        return False

    # Step 2: Exchange code for tokens
    print("\n📋 Step 3: Exchanging code for tokens...")

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
        expires_in = result.get("expires_in")  # seconds until access token expires

        if not access_token or not refresh_token:
            print("❌ Failed to get tokens!")
            print(f"Response: {result}")
            return False

        # Calculate expiration time for access token
        expires_at = None
        if expires_in:
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
            expires_at_str = expires_at.isoformat()
        else:
            expires_at_str = "Unknown (not provided by Google)"

        # Success!
        print("\n✅ Successfully obtained tokens!")
        print(f"\n📊 Token Information:")
        print(f"   Access Token: {access_token[:20]}...")
        print(f"   Refresh Token: {refresh_token[:20]}...")
        print(f"   Access Token Expires: {expires_at_str}")

        # Ask if user wants to store in database
        print("\n💾 Storage Options:")
        print("1. Store directly in database (recommended)")
        print("2. Save to file for manual storage")
        storage_choice = input("\nChoose option (1 or 2, default: 1): ").strip() or "1"

        if storage_choice == "1":
            # Try to store in database
            try:
                # Import here to avoid requiring db connection if user chooses file option
                from fitness.db.oauth_credentials import (
                    OAuthCredentials,
                    upsert_credentials,
                )

                credentials = OAuthCredentials(
                    provider="google",
                    client_id=client_id,
                    client_secret=client_secret,
                    access_token=access_token,
                    refresh_token=refresh_token,
                    expires_at=expires_at,
                )
                upsert_credentials(credentials)
                print("\n✅ Credentials stored in database!")
                print("🎉 Setup complete! You can now use Google Calendar sync.")
                return True
            except ImportError:
                print(
                    "\n⚠️  Could not import database modules. Make sure you're running from the project root."
                )
                print("   Falling back to file storage...")
                storage_choice = "2"
            except Exception as e:
                print(f"\n⚠️  Failed to store in database: {e}")
                print("   Falling back to file storage...")
                storage_choice = "2"

        if storage_choice == "2":
            # Save to file
            print("\n📝 Credentials (for manual database storage):")
            print("=" * 50)
            print(f"GOOGLE_CLIENT_ID={client_id}")
            print(f"GOOGLE_CLIENT_SECRET={client_secret}")
            print(f"GOOGLE_ACCESS_TOKEN={access_token}")
            print(f"GOOGLE_REFRESH_TOKEN={refresh_token}")
            if expires_at:
                print(f"GOOGLE_EXPIRES_AT={expires_at.isoformat()}")
            print("=" * 50)

            # Also save to a file for convenience
            with open("google_credentials.txt", "w") as f:
                f.write("# Google OAuth Credentials\n")
                f.write(f"# Access token expires at: {expires_at_str}\n\n")
                f.write(f"GOOGLE_CLIENT_ID={client_id}\n")
                f.write(f"GOOGLE_CLIENT_SECRET={client_secret}\n")
                f.write(f"GOOGLE_ACCESS_TOKEN={access_token}\n")
                f.write(f"GOOGLE_REFRESH_TOKEN={refresh_token}\n")
                if expires_at:
                    f.write(f"GOOGLE_EXPIRES_AT={expires_at.isoformat()}\n")

            print("\n💾 Credentials also saved to 'google_credentials.txt'")
            print("\n📋 To store in database, use:")
            print(
                "   from fitness.db.oauth_credentials import OAuthCredentials, upsert_credentials"
            )
            print("   from datetime import datetime, timezone")
            print(f"   credentials = OAuthCredentials(")
            print(f"       provider='google',")
            print(f"       client_id='{client_id}',")
            print(f"       client_secret='{client_secret}',")
            print(f"       access_token='{access_token}',")
            print(f"       refresh_token='{refresh_token}',")
            if expires_at:
                print(
                    f"       expires_at=datetime.fromisoformat('{expires_at.isoformat()}'),"
                )
            print(f"   )")
            print(f"   upsert_credentials(credentials)")

        print("\n🎉 Setup complete!")
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
            "\n🚀 Next step: Add the credentials to your .env.dev file and test the integration!"
        )
    else:
        print("\n❌ Setup failed. Please check the steps and try again.")
