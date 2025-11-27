/**
 * Authentication utilities for HTTP Basic Auth
 */

/**
 * Generate HTTP Basic Auth headers from username and password
 */
export function getAuthHeaders(
  username: string,
  password: string,
): HeadersInit {
  const credentials = btoa(`${username}:${password}`);
  return {
    Authorization: `Basic ${credentials}`,
  };
}

/**
 * Test credentials by calling a protected endpoint
 * @throws Error if credentials are invalid (401)
 */
export async function testCredentials(
  username: string,
  password: string,
): Promise<boolean> {
  // Test by calling the dedicated auth verification endpoint
  const testUrl = `${import.meta.env.VITE_API_URL}/auth/verify`;

  const res = await fetch(testUrl, {
    method: "GET",
    headers: getAuthHeaders(username, password),
  });

  if (res.status === 401) {
    throw new Error("Invalid credentials");
  }

  if (!res.ok) {
    throw new Error(`Auth verification failed: ${res.statusText}`);
  }

  return true;
}

/**
 * Check if auth credentials are configured
 */
export function isAuthConfigured(auth?: {
  username: string;
  password: string;
}): boolean {
  return !!(auth?.username && auth?.password);
}
