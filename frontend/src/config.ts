/**
 * MediKiosk Frontend Environment Configuration.
 *
 * Centralizes environment variable access with type-safe defaults.
 * In development, the Vite dev server proxies /api to the backend,
 * so API_BASE_URL defaults to empty string (same-origin).
 */

export const config = {
  /** Base URL for backend API calls. Empty string uses same-origin (Vite proxy in dev). */
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? '',

  /** Application name. */
  appName: 'MediKiosk',

  /** Current environment. */
  env: import.meta.env.MODE,

  /** Whether we're in development mode. */
  isDev: import.meta.env.DEV,
} as const
