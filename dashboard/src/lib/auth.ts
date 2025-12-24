const identityUrl = import.meta.env.VITE_IDENTITY_URL;
const clientId = import.meta.env.VITE_IDENTITY_CLIENT_ID;
const redirectUri = import.meta.env.VITE_BASE_URL + "/oauth/callback";

// Storage keys for OAuth state
const CODE_VERIFIER_KEY = "oauth_code_verifier";
const OAUTH_STATE_KEY = "oauth_state";

/**
 * Generate a cryptographically random string for PKCE
 */
function generateCodeVerifier(): string {
  const array = new Uint8Array(32);
  crypto.getRandomValues(array);
  // Convert to base64url
  return btoa(String.fromCharCode(...array))
    .replace(/=/g, "")
    .replace(/\+/g, "-")
    .replace(/\//g, "_");
}

/**
 * Generate code challenge from verifier using SHA-256 (S256 method)
 */
async function generateCodeChallenge(verifier: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(verifier);
  const digest = await crypto.subtle.digest("SHA-256", data);
  // Convert to base64url
  return btoa(String.fromCharCode(...new Uint8Array(digest)))
    .replace(/=/g, "")
    .replace(/\+/g, "-")
    .replace(/\//g, "_");
}

export async function oauthAuthorizeUrl(): Promise<string> {
  const state = crypto.randomUUID();
  const codeChallengeMethod = "S256";
  const codeVerifier = generateCodeVerifier();
  const codeChallenge = await generateCodeChallenge(codeVerifier);

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
  const identityUrl = import.meta.env.VITE_IDENTITY_URL;
  
  // OAuth token endpoints typically expect application/x-www-form-urlencoded
  // This format often avoids CORS preflight requests
  const params = new URLSearchParams();
  params.set("grant_type", "authorization_code");
  params.set("code", code);
  params.set("code_verifier", codeVerifier);
  params.set("redirect_uri", redirectUri);
  params.set("client_id", clientId);

  const response = await fetch(`${identityUrl}/token`, {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: params.toString(),
  });

  if (!response.ok) {
    const errorText = await response.text().catch(() => response.statusText);
    throw new Error(`Token exchange failed: ${errorText}`);
  }

  return response.json();
}