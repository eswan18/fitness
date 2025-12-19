import { useEffect, useState } from "react";
import {
  parseOAuthCallback,
  getStoredCodeVerifier,
  getStoredOAuthState,
  clearStoredOAuthData,
  exchangeCodeForTokens,
} from "@/lib/auth";
import { useDashboardStore } from "@/store";
import { notifySuccess, notifyError } from "@/lib/errors";

/**
 * OAuth callback handler component
 * Only activates when the URL path is /oauth/callback
 * Handles the OAuth authorization code exchange flow
 */
export function OAuthCallbackHandler() {
  const { setCredentials } = useDashboardStore();
  const [status, setStatus] = useState<"processing" | "success" | "error">(
    "processing",
  );
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    // Only handle if we're on the callback route and not already complete
    if (window.location.pathname !== "/oauth/callback" || isComplete) {
      return;
    }

    const handleCallback = async () => {
      try {
        const callback = parseOAuthCallback();

        // Check for OAuth error
        if (callback.error) {
          throw new Error(
            `OAuth authorization failed: ${callback.error}`,
          );
        }

        // Validate we have required parameters
        if (!callback.code || !callback.state) {
          throw new Error("Missing required OAuth parameters");
        }

        // Validate state parameter (CSRF protection)
        const storedState = getStoredOAuthState();
        if (!storedState) {
          throw new Error("OAuth state not found. Please try logging in again.");
        }

        if (storedState !== callback.state) {
          throw new Error(
            "Invalid state parameter. Possible CSRF attack or expired session.",
          );
        }

        // Get code verifier
        const codeVerifier = getStoredCodeVerifier();
        if (!codeVerifier) {
          throw new Error(
            "Code verifier not found. Please try logging in again.",
          );
        }

        // Exchange code for tokens
        const tokens = await exchangeCodeForTokens(
          callback.code,
          codeVerifier,
        );

        // Store authentication
        // Using access_token as password for now - adjust based on your backend's needs
        // You may want to update your store to handle OAuth tokens differently
        setCredentials("oauth_user", tokens.access_token);

        // Clean up OAuth data
        clearStoredOAuthData();

        setStatus("success");
        notifySuccess("Logged in successfully!");

        // Clean up URL and navigate to dashboard
        // AuthGate will automatically show the dashboard since isAuthenticated is now true
        setTimeout(() => {
          window.history.replaceState({}, "", "/");
          setIsComplete(true); // Mark as complete so component stops rendering
        }, 1000);
      } catch (err) {
        const error =
          err instanceof Error ? err.message : "An unknown error occurred";
        setErrorMessage(error);
        setStatus("error");
        notifyError(err, "OAuth login failed");

        // Clean up on error
        clearStoredOAuthData();

        // Clean up URL
        window.history.replaceState({}, "", "/");
      }
    };

    handleCallback();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [setCredentials]);

  // Only render if we're on the callback route and not complete
  if (window.location.pathname !== "/oauth/callback" || isComplete) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="text-center space-y-4">
        {status === "processing" && (
          <>
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto" />
            <p className="text-muted-foreground">Completing login...</p>
          </>
        )}
        {status === "success" && (
          <>
            <div className="text-green-600 dark:text-green-400 text-4xl">✓</div>
            <p className="text-foreground">Login successful! Redirecting...</p>
          </>
        )}
        {status === "error" && (
          <>
            <div className="text-red-600 dark:text-red-400 text-4xl">✗</div>
            <p className="text-foreground">Login failed</p>
            {errorMessage && (
              <p className="text-sm text-muted-foreground">{errorMessage}</p>
            )}
            <button
              onClick={() => (window.location.href = "/")}
              className="mt-4 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
            >
              Return to Home
            </button>
          </>
        )}
      </div>
    </div>
  );
}
