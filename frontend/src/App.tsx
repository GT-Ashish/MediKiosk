import React from 'react'
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
  const { currentRoute, appMode, goTo } = useKiosk()

  // If in Doctor Mode, show the physician review dashboard
  if (appMode === 'doctor') {
    return <DoctorDashboard />
  }

  // Otherwise, render the patient kiosk flow
  return (
    <div className="min-h-screen bg-[#F6F8F7] flex flex-col justify-between selection:bg-[#DCEDEA] selection:text-[#2F7D73]">
      {/* Top Header & Step Progress Bar */}
      <KioskHeader />

      {/* Main Screen Content */}
      <main className="flex-1 w-full max-w-5xl mx-auto p-4 flex flex-col justify-center">
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

      {/* Minimal Bottom Bar with Demo Navigation Shortcut */}
      <footer className="w-full py-2 px-6 border-t border-[#D9E2DF] bg-white text-center text-xs text-[#647471] flex flex-wrap items-center justify-between gap-2">
        <span>MediKiosk SIH 2026 • AI-Powered Clinical History Platform</span>
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-semibold text-[#647471]">Quick Jump (Demo):</span>
          <select
            value={currentRoute}
            onChange={(e) => goTo(e.target.value as any)}
            className="text-[11px] font-medium bg-[#F6F8F7] border border-[#D9E2DF] rounded px-2 py-0.5 text-[#243331] outline-none"
          >
            <option value="language">1. Language</option>
            <option value="consent">2. Consent</option>
            <option value="identification">3. Identification</option>
            <option value="visit_reason">4. Visit Reason</option>
            <option value="complaint">5. Chief Complaint (New)</option>
            <option value="history_taking">6. History Taking (New)</option>
            <option value="documents">7. Documents</option>
            <option value="review">8. Review Summary</option>
            <option value="confirmation">9. Confirmation</option>
            <option value="follow_up">10. Follow-up Visits</option>
          </select>
        </div>
      </footer>
    </div>
  )
}

function App() {
  return (
    <KioskProvider>
      <KioskApp />
    </KioskProvider>
  )
}

export default App
