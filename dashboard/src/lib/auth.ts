const identityUrl = import.meta.env.VITE_IDENTITY_URL;
const clientId = import.meta.env.VITE_IDENTITY_CLIENT_ID;
const redirectUri = import.meta.env.VITE_BASE_URL + "/oauth/callback";

// Storage keys for OAuth state
const CODE_VERIFIER_KEY = "oauth_code_verifier";
const OAUTH_STATE_KEY = "oauth_state";

export function oauthAuthorizeUrl() {
  const state = crypto.randomUUID();
  const codeChallengeMethod = "S256";
  const codeVerifier = crypto.randomUUID();
  const codeChallenge = btoa(codeVerifier).replace(/=/g, "").replace(/\+/g, "-").replace(/\//g, "_");

  // Store the code verifier and state in local storage
  localStorage.setItem(CODE_VERIFIER_KEY, codeVerifier);
  localStorage.setItem(OAUTH_STATE_KEY, state);

  const authUrl = new URL(`${identityUrl}/authorize`);

  authUrl.searchParams.set("redirect_uri", redirectUri);
  authUrl.searchParams.set("response_type", "code");
  authUrl.searchParams.set("client_id", clientId);
  authUrl.searchParams.set("scope", "openid profile email");
  authUrl.searchParams.set("code_challenge", codeChallenge);
  authUrl.searchParams.set("code_challenge_method", codeChallengeMethod);
  authUrl.searchParams.set("state", state);
  return authUrl.toString();
}


/**
 * Get stored code verifier (for token exchange)
 */
export function getStoredCodeVerifier(): string | null {
  return localStorage.getItem(CODE_VERIFIER_KEY);
}

/**
 * Get stored OAuth state (for validation)
 */
export function getStoredOAuthState(): string | null {
  return localStorage.getItem(OAUTH_STATE_KEY);
}

/**
 * Clear stored OAuth data
 */
export function clearStoredOAuthData(): void {
  localStorage.removeItem(CODE_VERIFIER_KEY);
  localStorage.removeItem(OAUTH_STATE_KEY);
}

/**
 * Extract OAuth callback parameters from URL
 */
export function parseOAuthCallback(): {
  code: string | null;
  state: string | null;
  error: string | null;
} {
  const params = new URLSearchParams(window.location.search);
  return {
    code: params.get("code"),
    state: params.get("state"),
    error: params.get("error"),
  };
}

/**
 * Exchange authorization code for tokens
 * You'll need to create this endpoint on your backend
 */
export async function exchangeCodeForTokens(
  code: string,
  codeVerifier: string,
): Promise<{ access_token: string; id_token?: string }> {
  const apiUrl = import.meta.env.VITE_API_URL;
  const response = await fetch(`${apiUrl}/oauth/callback`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      code,
      code_verifier: codeVerifier,
      redirect_uri: redirectUri,
    }),
  });

  if (!response.ok) {
    throw new Error(`Token exchange failed: ${response.statusText}`);
  }

  return response.json();
}