/**
 * MediKiosk — Application Shell.
 *
 * This is the root application component. Currently displays the project
 * status page with backend health check. The actual patient-facing UI
 * (conversational history, document scanning, etc.) will be built later.
 */

import { HealthStatus } from './components/HealthStatus'

function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-surface-50 via-primary-50/30 to-surface-100">
      {/* Header */}
      <header className="border-b border-surface-200/60 bg-white/60 backdrop-blur-md sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center text-white font-bold text-sm shadow-md">
              M
            </div>
            <div>
              <h1 className="text-lg font-bold text-surface-900 leading-tight">
                MediKiosk
              </h1>
              <p className="text-xs text-surface-500 leading-tight">
                AI Clinical History Platform
              </p>
            </div>
          </div>
          <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-amber-100 text-amber-800 border border-amber-200">
            Development
          </span>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-6 py-12">
        <div className="text-center mb-12 animate-fade-in">
          <h2 className="text-3xl font-bold text-surface-900 mb-3">
            Project Status
          </h2>
          <p className="text-surface-500 max-w-xl mx-auto">
            MediKiosk is under active development. This page verifies that the
            frontend and backend services are running and connected.
          </p>
        </div>

        {/* Health Check Card */}
        <div className="animate-fade-in" style={{ animationDelay: '0.15s', animationFillMode: 'backwards' }}>
          <HealthStatus />
        </div>

        {/* Module Status Grid */}
        <div className="mt-12 animate-fade-in" style={{ animationDelay: '0.3s', animationFillMode: 'backwards' }}>
          <h3 className="text-sm font-semibold text-surface-500 uppercase tracking-wider mb-4 text-center">
            Module Status
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { label: 'History Engine', icon: '🎙️', status: 'Planned' },
              { label: 'Document AI', icon: '📄', status: 'Planned' },
              { label: 'Summary Gen', icon: '📋', status: 'Planned' },
              { label: 'ABDM Integration', icon: '🔗', status: 'Pending Review' },
            ].map((mod) => (
              <div
                key={mod.label}
                className="rounded-xl border border-surface-200 bg-white/60 backdrop-blur-sm p-4 text-center"
              >
                <span className="text-2xl mb-2 block">{mod.icon}</span>
                <p className="text-sm font-semibold text-surface-800">{mod.label}</p>
                <span className="inline-block mt-1.5 text-xs font-medium px-2 py-0.5 rounded-full bg-surface-100 text-surface-500">
                  {mod.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-surface-200/60 bg-white/40 mt-12">
        <div className="max-w-5xl mx-auto px-6 py-4 text-center text-xs text-surface-400">
          MediKiosk — SIH 2026 · AI-Powered Clinical History Software Platform
        </div>
      </footer>
    </div>
  )
}

export default App
