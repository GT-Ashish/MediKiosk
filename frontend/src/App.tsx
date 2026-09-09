import React, { useState, useEffect } from 'react'
import { KioskProvider, useKiosk } from './context/KioskContext'
import { KioskHeader } from './components/patient/KioskHeader'
import { LanguagePage } from './pages/patient/LanguagePage'
import { ConsentPage } from './pages/patient/ConsentPage'
import { IdentificationPage } from './pages/patient/IdentificationPage'
import { VisitReasonPage } from './pages/patient/VisitReasonPage'
import { ComplaintPage } from './pages/patient/ComplaintPage'
import { HistoryTakingPage } from './pages/patient/HistoryTakingPage'
import { DocumentsPage } from './pages/patient/DocumentsPage'
import { ReviewSummaryPage } from './pages/patient/ReviewSummaryPage'
import { ConfirmationPage } from './pages/patient/ConfirmationPage'
import { FollowUpPage } from './pages/patient/FollowUpPage'
import { DoctorDashboard } from './pages/doctor/DoctorDashboard'

const KioskApp: React.FC = () => {
  const { currentRoute } = useKiosk()

  // Render the sequential patient kiosk flow
  return (
    <div className="h-screen bg-[#F6F8F7] flex flex-col justify-between selection:bg-[#DCEDEA] selection:text-[#2F7D73] overflow-hidden">
      {/* Top Header & Step Progress Bar */}
      <KioskHeader />

      {/* Main Screen Content */}
      <main className="flex-1 min-h-0 w-full max-w-5xl mx-auto px-4 py-1.5 flex flex-col justify-center overflow-hidden">
        {currentRoute === 'language' && <LanguagePage />}
        {currentRoute === 'consent' && <ConsentPage />}
        {currentRoute === 'identification' && <IdentificationPage />}
        {currentRoute === 'visit_reason' && <VisitReasonPage />}
        {currentRoute === 'complaint' && <ComplaintPage />}
        {currentRoute === 'history_taking' && <HistoryTakingPage />}
        {currentRoute === 'documents' && <DocumentsPage />}
        {currentRoute === 'review' && <ReviewSummaryPage />}
        {currentRoute === 'confirmation' && <ConfirmationPage />}
        {currentRoute === 'follow_up' && <FollowUpPage />}
      </main>

      {/* Clean Bottom Footer Bar (Quick Jump completely removed) */}
      <footer className="w-full py-2.5 px-6 border-t border-[#D9E2DF] bg-white text-center text-xs text-[#647471] flex items-center justify-between flex-shrink-0">
        <span>MediKiosk SIH 2026 • AI-Powered Clinical History Platform</span>
        <span className="text-[11px] text-[#8C9E9A]">Patient Terminal Active</span>
      </footer>
    </div>
  )
}

function App() {
  const [currentPath, setCurrentPath] = useState(() => window.location.pathname)

  useEffect(() => {
    const handleLocationChange = () => {
      setCurrentPath(window.location.pathname)
    }

    window.addEventListener('popstate', handleLocationChange)
    return () => {
      window.removeEventListener('popstate', handleLocationChange)
    }
  }, [])

  // Route /dev/doctor strictly to the Doctor Dashboard
  if (currentPath.startsWith('/dev/doctor')) {
    return (
      <KioskProvider>
        <DoctorDashboard />
      </KioskProvider>
    )
  }

  // Root / route serves patient kiosk
  return (
    <KioskProvider>
      <KioskApp />
    </KioskProvider>
  )
}

export default App

