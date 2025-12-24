"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import {
  getStoredCodeVerifier,
  getStoredOAuthState,
  clearStoredOAuthData,
  exchangeCodeForTokens,
} from "@/lib/auth";
import { useDashboardStore } from "@/store";
import { notifySuccess, notifyError } from "@/lib/errors";

function OAuthCallbackContent() {
  const { setCredentials } = useDashboardStore();
  const searchParams = useSearchParams();
  const router = useRouter();
  const [status, setStatus] = useState<"processing" | "success" | "error">(
    "processing",
  );
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [hasProcessed, setHasProcessed] = useState(false);

  useEffect(() => {
    // Prevent processing the callback multiple times
    if (hasProcessed) {
      return;
    }

    const handleCallback = async () => {
      setHasProcessed(true);
      try {
        // Get OAuth callback parameters from URL
        const code = searchParams.get("code");
        const state = searchParams.get("state");
        const error = searchParams.get("error");

        // Check for OAuth error
        if (error) {
          throw new Error(`OAuth authorization failed: ${error}`);
        }

        // Validate we have required parameters
        if (!code || !state) {
          throw new Error("Missing required OAuth parameters");
        }

        // Validate state parameter (CSRF protection)
        const storedState = getStoredOAuthState();
        if (!storedState) {
          throw new Error("OAuth state not found. Please try logging in again.");
        }

        if (storedState !== state) {
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
        const tokens = await exchangeCodeForTokens(code, codeVerifier);

        // Store authentication
        setCredentials("oauth_user", tokens.access_token);

        // Clean up OAuth data
        clearStoredOAuthData();

        setStatus("success");
        notifySuccess("Logged in successfully!");

        // Navigate to dashboard after a brief delay
        setTimeout(() => {
          router.replace("/");
        }, 1000);
      } catch (err) {
        const error =
          err instanceof Error ? err.message : "An unknown error occurred";
        console.error("OAuth callback error:", err);
        setErrorMessage(error);
        setStatus("error");
        notifyError(err, "OAuth login failed");

        // Clean up on error
        clearStoredOAuthData();
      }
    };

    handleCallback();
  }, [setCredentials, searchParams, router, hasProcessed]);

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
              onClick={() => router.replace("/")}
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

export default function OAuthCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-background flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto" />
        </div>
      }
    >
      <OAuthCallbackContent />
    </Suspense>
  );
}
