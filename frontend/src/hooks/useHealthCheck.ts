/**
 * useHealthCheck Hook.
 *
 * Custom React hook that fetches and manages the backend health status.
 * Handles loading, success, and error states.
 */

import { useState, useEffect, useCallback } from 'react'
import { fetchHealthStatus, type HealthStatus } from '../services/api'

interface UseHealthCheckResult {
  /** The health status data, or null if not yet loaded / errored. */
  data: HealthStatus | null
  /** Whether the request is currently in flight. */
  loading: boolean
  /** Error message if the request failed, or null. */
  error: string | null
  /** Manually re-fetch the health status. */
  refetch: () => void
}

export function useHealthCheck(): UseHealthCheckResult {
  const [data, setData] = useState<HealthStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchHealth = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const result = await fetchHealthStatus()
      setData(result)
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'Failed to connect to the backend'
      setError(message)
      setData(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchHealth()
  }, [fetchHealth])

  return { data, loading, error, refetch: fetchHealth }
}
