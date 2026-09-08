/**
 * HealthStatus Component.
 *
 * Displays the backend health status with loading, success, and error states.
 * This is a development/status component used to verify frontend↔backend connectivity.
 */

import { useHealthCheck } from '../hooks/useHealthCheck'

export function HealthStatus() {
  const { data, loading, error, refetch } = useHealthCheck()

  return (
    <div className="w-full max-w-lg mx-auto">
      <div className="rounded-2xl border border-surface-200 bg-white/80 backdrop-blur-sm shadow-lg overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-surface-200 bg-surface-50/50">
          <h2 className="text-lg font-semibold text-surface-800 flex items-center gap-2">
            <span className="text-xl">🔗</span>
            Backend Connection
          </h2>
        </div>

        {/* Body */}
        <div className="p-6">
          {loading && (
            <div className="flex items-center gap-3 text-surface-500" id="health-loading">
              <div className="w-5 h-5 border-2 border-primary-400 border-t-transparent rounded-full animate-spin" />
              <span>Connecting to backend...</span>
            </div>
          )}

          {error && (
            <div className="space-y-4" id="health-error">
              <div className="flex items-center gap-3 text-error">
                <span className="text-2xl">✗</span>
                <div>
                  <p className="font-medium">Backend Unavailable</p>
                  <p className="text-sm text-surface-500 mt-0.5">{error}</p>
                </div>
              </div>
              <p className="text-xs text-surface-400">
                Make sure the FastAPI server is running on port 8000.
              </p>
            </div>
          )}

          {data && (
            <div className="space-y-3" id="health-success">
              <div className="flex items-center gap-3">
                <span className="relative flex h-3 w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-success opacity-75" />
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-success" />
                </span>
                <span className="font-medium text-success">Connected</span>
              </div>

              <dl className="grid grid-cols-2 gap-x-4 gap-y-2 text-sm mt-4">
                <dt className="text-surface-500">Service</dt>
                <dd className="text-surface-800 font-medium">{data.app_name}</dd>

                <dt className="text-surface-500">Version</dt>
                <dd className="text-surface-800 font-mono text-xs mt-0.5">{data.version}</dd>

                <dt className="text-surface-500">Environment</dt>
                <dd>
                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                    {data.environment}
                  </span>
                </dd>

                <dt className="text-surface-500">Status</dt>
                <dd>
                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    {data.status}
                  </span>
                </dd>

                <dt className="text-surface-500">Last Check</dt>
                <dd className="text-surface-800 font-mono text-xs mt-0.5">
                  {new Date(data.timestamp).toLocaleTimeString()}
                </dd>
              </dl>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-surface-200 bg-surface-50/50">
          <button
            onClick={refetch}
            disabled={loading}
            id="health-refetch-btn"
            className="text-sm font-medium text-primary-600 hover:text-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors cursor-pointer"
          >
            {loading ? 'Checking...' : '↻ Refresh Status'}
          </button>
        </div>
      </div>
    </div>
  )
}
