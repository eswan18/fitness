function getIdentityUrl(): string {
  return process.env.NEXT_PUBLIC_IDENTITY_URL || "";
}

function getClientId(): string {
  return process.env.NEXT_PUBLIC_IDENTITY_CLIENT_ID || "";
}

function getRedirectUri(): string {
  const baseUrl =
    typeof window !== "undefined"
      ? process.env.NEXT_PUBLIC_BASE_URL || window.location.origin
      : process.env.NEXT_PUBLIC_BASE_URL || "";
  return `${baseUrl}/oauth/callback`;
}

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
  // Ensure we're in browser context
  if (typeof window === "undefined") {
    throw new Error("oauthAuthorizeUrl can only be called in browser context");
  }

  const state = crypto.randomUUID();
  const codeChallengeMethod = "S256";
  const codeVerifier = generateCodeVerifier();
  const codeChallenge = await generateCodeChallenge(codeVerifier);

  // Store the code verifier and state in local storage
  localStorage.setItem(CODE_VERIFIER_KEY, codeVerifier);
  localStorage.setItem(OAUTH_STATE_KEY, state);

  const currentIdentityUrl = getIdentityUrl();
  const currentClientId = getClientId();
  const currentRedirectUri = getRedirectUri();

  if (!currentIdentityUrl || !currentClientId) {
    throw new Error("Identity provider configuration missing");
  }

  const authUrl = new URL(`${currentIdentityUrl}/authorize`);

  authUrl.searchParams.set("redirect_uri", currentRedirectUri);
  authUrl.searchParams.set("response_type", "code");
  authUrl.searchParams.set("client_id", currentClientId);
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
  if (typeof window === "undefined") return null;
  return localStorage.getItem(CODE_VERIFIER_KEY);
}

/**
 * Get stored OAuth state (for validation)
 */
export function getStoredOAuthState(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(OAUTH_STATE_KEY);
}

/**
 * Clear stored OAuth data
 */
export function clearStoredOAuthData(): void {
  if (typeof window === "undefined") return;
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
  // Call our backend API route instead of the identity provider directly
  // This avoids CORS issues and keeps the token exchange secure
  const apiUrl =
    typeof window !== "undefined"
      ? process.env.NEXT_PUBLIC_API_URL || window.location.origin
      : process.env.NEXT_PUBLIC_API_URL || "";

  const response = await fetch(`${apiUrl}/api/oauth/callback`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      code,
      code_verifier: codeVerifier,
      redirect_uri: getRedirectUri(),
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(async () => ({
      error: await response.text().catch(() => response.statusText),
    }));
    throw new Error(
      `Token exchange failed: ${errorData.error || errorData.details || "Unknown error"}`,
    );
  }

  const tokenData = await response.json();

  if (!tokenData.access_token) {
    throw new Error(
      `Token exchange succeeded but no access_token in response: ${JSON.stringify(tokenData)}`,
    );
  }

  return tokenData;
}