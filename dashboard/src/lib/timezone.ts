/**
 * Get the user's local timezone using the Intl API.
 * Returns the IANA timezone identifier (e.g., "America/Chicago", "Europe/London").
 */
export function getUserTimezone(): string {
  return Intl.DateTimeFormat().resolvedOptions().timeZone;
}