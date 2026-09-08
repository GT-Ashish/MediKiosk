/**
 * Health API Service.
 *
 * Provides a typed client for the backend health check endpoint.
 * This is the first API service — it validates frontend↔backend connectivity.
 */

import { config } from '../config'

export interface HealthStatus {
  status: string
  app_name: string
  version: string
  environment: string
  timestamp: string
}

/**
 * Fetches the backend health status from GET /api/health.
 *
 * @throws {Error} If the backend is unreachable or returns a non-OK response.
 */
export async function fetchHealthStatus(): Promise<HealthStatus> {
  const response = await fetch(`${config.apiBaseUrl}/api/health`)

  if (!response.ok) {
    throw new Error(`Backend returned ${response.status}: ${response.statusText}`)
  }

  return response.json()
}
