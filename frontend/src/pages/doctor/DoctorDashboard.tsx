import React, { useState } from 'react'
import { useKiosk } from '../../context/KioskContext'
import { MOCK_DOCTOR_QUEUE } from '../../data/mockData'
import type { DoctorQueuePatient } from '../../types'
import { HealthStatus } from '../../components/HealthStatus'

export const DoctorDashboard: React.FC = () => {
  const { setAppMode, clinicalSummary } = useKiosk()

  // Initialize queue with mock data, ensuring Token A 102 syncs with any edits made in kiosk
  const [queue, setQueue] = useState<DoctorQueuePatient[]>(() => {
    return MOCK_DOCTOR_QUEUE.map((item) => {
      if (item.tokenNumber === 'A 102') {
        return {
          ...item,
          historySummary: clinicalSummary,
        }
      }
      return item
    })
  })

  const [selectedToken, setSelectedToken] = useState<string>('A 102')
  const [isEditingDraft, setIsEditingDraft] = useState(false)
  const [editedComplaint, setEditedComplaint] = useState(clinicalSummary.chiefComplaint)
  const [physicianNotes, setPhysicianNotes] = useState('')
  const [showHealthModal, setShowHealthModal] = useState(false)

  const selectedPatient = queue.find((p) => p.tokenNumber === selectedToken) || queue[0]

  const handleConfirmDraft = (token: string) => {
    setQueue((prev) =>
      prev.map((p) => {
        if (p.tokenNumber === token) {
          return {
            ...p,
            status: 'Completed',
            historySummary: {
              ...p.historySummary,
              chiefComplaint: editedComplaint,
              reviewStatus: 'confirmed',
              physicianNotes,
            },
          }
        }
        return p
      })
    )
    setIsEditingDraft(false)
  }

  const handleRejectDraft = (token: string) => {
    setQueue((prev) =>
      prev.map((p) => {
        if (p.tokenNumber === token) {
          return {
            ...p,
            historySummary: {
              ...p.historySummary,
              reviewStatus: 'rejected',
            },
          }
        }
        return p
      })
    )
  }

  return (
    <div className="min-h-screen bg-[#F6F8F7] text-[#243331] flex flex-col font-sans">
      {/* Doctor Portal Header */}
      <header className="bg-white border-b border-[#D9E2DF] px-6 py-3.5 sticky top-0 z-20 shadow-xs">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-[#2F7D73] text-white flex items-center justify-center font-bold text-sm">
              Dr
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-lg font-bold text-[#243331]">
                  Physician OPD Console
                </h1>
                <span className="text-[11px] font-semibold px-2 py-0.5 rounded bg-[#DCEDEA] text-[#2F7D73]">
                  Room 4 • Gastroenterology
                </span>
              </div>
              <p className="text-xs text-[#647471]">
                Dr. S. Mehta, MD • MediKiosk EHR Bridge
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* System Status / Health Check */}
            <button
              type="button"
              onClick={() => setShowHealthModal(true)}
              className="px-3 py-1.5 rounded-lg border border-[#D9E2DF] text-xs font-semibold text-[#647471] hover:bg-gray-50 flex items-center gap-1.5 cursor-pointer"
            >
              <span className="w-2 h-2 rounded-full bg-[#4F8A6D]" />
              <span>System Status</span>
            </button>

            {/* Switch back to Kiosk Mode */}
            <button
              type="button"
              onClick={() => {
                setAppMode('kiosk')
                window.history.pushState({}, '', '/')
                window.dispatchEvent(new PopStateEvent('popstate'))
              }}
              className="px-3.5 py-1.5 bg-[#2F7D73] hover:bg-[#276B63] text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 cursor-pointer shadow-xs transition-colors"
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              <span>Back to Patient Kiosk</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Grid: Left Queue (1/3) + Right Patient Record (2/3) */}
      <main className="max-w-7xl mx-auto w-full p-4 sm:p-6 grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1">
        {/* Left Side: OPD Patient Queue (4 cols) */}
        <section className="lg:col-span-4 bg-white border border-[#D9E2DF] rounded-2xl shadow-xs overflow-hidden flex flex-col h-[calc(100vh-130px)]">
          <div className="p-4 border-b border-[#D9E2DF] bg-[#F6F8F7] flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-[#243331]">Patient Queue</h2>
              <p className="text-xs text-[#647471]">
                Today's Intakes ({queue.length} Total)
              </p>
            </div>
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-white text-[#2F7D73] border border-[#D9E2DF]">
              Live Feed
            </span>
          </div>

          <div className="overflow-y-auto divide-y divide-[#EBF0EE] flex-1">
            {queue.map((item) => {
              const isSelected = item.tokenNumber === selectedToken

              return (
                <button
                  key={item.tokenNumber}
                  type="button"
                  onClick={() => {
                    setSelectedToken(item.tokenNumber)
                    setEditedComplaint(item.historySummary.chiefComplaint)
                    setIsEditingDraft(false)
                  }}
                  className={`w-full p-4 text-left transition-colors cursor-pointer flex flex-col gap-1.5 ${
                    isSelected
                      ? 'bg-[#DCEDEA]/40 border-l-4 border-[#2F7D73]'
                      : 'hover:bg-[#F9FBFA]'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-base font-black font-mono text-[#243331]">
                      {item.tokenNumber}
                    </span>
                    <div className="flex items-center gap-1.5">
                      {item.isRedFlag && (
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#F9EBEB] text-[#B85C5C] border border-[#B85C5C]/30 animate-pulse">
                          🚨 Priority Alert
                        </span>
                      )}
                      <span
                        className={`text-[11px] font-semibold px-2 py-0.5 rounded-full ${
                          item.status === 'Completed'
                            ? 'bg-[#EBF4EE] text-[#4F8A6D]'
                            : item.status === 'In Consultation'
                            ? 'bg-[#EFF6FF] text-[#2563EB]'
                            : 'bg-[#FBF4E8] text-[#B8874A]'
                        }`}
                      >
                        {item.status}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <p className="text-sm font-bold text-[#243331]">
                      {item.patientName}
                    </p>
                    <span className="text-xs text-[#647471]">
                      {item.arrivalTime}
                    </span>
                  </div>

                  <p className="text-xs text-[#647471] truncate">
                    {item.complaint}
                  </p>
                </button>
              )
            })}
          </div>
        </section>

        {/* Right Side: Selected Patient Record & AI Draft (8 cols) */}
        <section className="lg:col-span-8 bg-white border border-[#D9E2DF] rounded-2xl shadow-xs overflow-hidden flex flex-col h-[calc(100vh-130px)]">
          {/* Patient Details Header */}
          <div className="p-5 border-b border-[#D9E2DF] bg-[#F6F8F7] flex flex-wrap items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-3">
                <h2 className="text-xl font-bold text-[#243331]">
                  {selectedPatient.patientName}
                </h2>
                <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-white text-[#2F7D73] border border-[#D9E2DF]">
                  Token: {selectedPatient.tokenNumber}
                </span>
                <span className="text-xs text-[#647471]">
                  {selectedPatient.ageGender}
                </span>
              </div>
              <p className="text-xs text-[#647471] mt-0.5">
                Visit Category: <strong className="text-[#243331]">{selectedPatient.visitType}</strong> • Intake Time: {selectedPatient.arrivalTime}
              </p>
            </div>

            {/* Review Status Badge */}
            <div>
              {selectedPatient.historySummary.reviewStatus === 'confirmed' ? (
                <span className="px-3 py-1 rounded-full text-xs font-bold bg-[#EBF4EE] text-[#4F8A6D] border border-[#4F8A6D]/30 flex items-center gap-1.5">
                  ✓ Confirmed by Physician
                </span>
              ) : selectedPatient.historySummary.reviewStatus === 'rejected' ? (
                <span className="px-3 py-1 rounded-full text-xs font-bold bg-[#F9EBEB] text-[#B85C5C] border border-[#B85C5C]/30 flex items-center gap-1.5">
                  ✕ Returned / Rejected
                </span>
              ) : (
                <span className="px-3 py-1 rounded-full text-xs font-bold bg-[#FBF4E8] text-[#B8874A] border border-[#B8874A]/30 flex items-center gap-1.5">
                  ✎ Draft Requiring Review
                </span>
              )}
            </div>
          </div>

          {/* Emergency Priority Alert (Mock Red Flag) */}
          {selectedPatient.isRedFlag && selectedPatient.redFlagReason && (
            <div className="p-4 bg-[#F9EBEB] border-b border-[#B85C5C]/20 flex items-start gap-3">
              <span className="text-xl">⚠️</span>
              <div>
                <p className="text-sm font-bold text-[#B85C5C]">
                  Clinical Triage Alert — Immediate Physician Attention
                </p>
                <p className="text-xs text-[#B85C5C]/90 mt-0.5">
                  {selectedPatient.redFlagReason}
                </p>
              </div>
            </div>
          )}

          {/* Scrollable Content: AI Draft + History + Documents */}
          <div className="overflow-y-auto p-6 space-y-6 flex-1">
            {/* Box 1: AI-Generated Draft Section */}
            <div className="border-2 border-[#2F7D73]/30 rounded-2xl p-5 bg-[#F9FBFA] relative">
              {/* Mandatory Prominent Watermark Banner */}
              <div className="flex items-center justify-between pb-3 mb-4 border-b border-[#D9E2DF]">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#2F7D73]" />
                  <h3 className="text-sm font-bold uppercase tracking-wider text-[#2F7D73]">
                    AI-Generated Draft — Physician Review Required
                  </h3>
                </div>
                <span className="text-[11px] text-[#647471] italic">
                  Non-autonomous history elicitation
                </span>
              </div>

              {/* Chief Complaint & HPI */}
              <div className="space-y-4">
                <div>
                  <label className="text-xs font-bold uppercase tracking-wider text-[#647471] block mb-1">
                    Chief Complaint & Narration:
                  </label>
                  {isEditingDraft ? (
                    <textarea
                      value={editedComplaint}
                      onChange={(e) => setEditedComplaint(e.target.value)}
                      className="w-full p-3 bg-white border border-[#2F7D73] rounded-xl text-sm text-[#243331] outline-none"
                      rows={3}
                    />
                  ) : (
                    <p className="text-base font-semibold text-[#243331] bg-white p-3.5 rounded-xl border border-[#D9E2DF]">
                      {editedComplaint}
                    </p>
                  )}
                </div>

                {/* Structured Key Points */}
                <div>
                  <label className="text-xs font-bold uppercase tracking-wider text-[#647471] block mb-1">
                    Structured Clinical History Points:
                  </label>
                  <ul className="space-y-1.5 bg-white p-3.5 rounded-xl border border-[#D9E2DF] text-sm text-[#243331]">
                    {selectedPatient.historySummary.keyPoints.map((point, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-[#2F7D73] font-bold">•</span>
                        <span>{point}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Physician Notes Input */}
                <div>
                  <label className="text-xs font-bold uppercase tracking-wider text-[#647471] block mb-1">
                    Physician Examination / Review Notes:
                  </label>
                  <input
                    type="text"
                    value={physicianNotes}
                    onChange={(e) => setPhysicianNotes(e.target.value)}
                    placeholder="Add clinical observations or modify before signing..."
                    className="w-full px-3.5 py-2.5 bg-white border border-[#D9E2DF] rounded-xl text-sm text-[#243331] outline-none focus:border-[#2F7D73]"
                  />
                </div>
              </div>

              {/* Physician Review Action Bar */}
              <div className="flex items-center justify-between pt-4 mt-5 border-t border-[#D9E2DF]">
                <button
                  type="button"
                  onClick={() => setIsEditingDraft(!isEditingDraft)}
                  className="px-4 py-2 border border-[#D9E2DF] bg-white hover:bg-gray-50 text-xs font-bold text-[#243331] rounded-xl transition-colors cursor-pointer"
                >
                  {isEditingDraft ? 'Done Editing' : '✎ Edit Draft'}
                </button>

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => handleRejectDraft(selectedPatient.tokenNumber)}
                    className="px-4 py-2 bg-[#B85C5C] hover:bg-[#9E4A4A] text-white text-xs font-bold rounded-xl transition-colors cursor-pointer"
                  >
                    Reject / Re-interview
                  </button>

                  <button
                    type="button"
                    onClick={() => handleConfirmDraft(selectedPatient.tokenNumber)}
                    className="px-5 py-2 bg-[#4F8A6D] hover:bg-[#3E6E56] text-white text-xs font-bold rounded-xl shadow-xs transition-colors cursor-pointer flex items-center gap-1.5"
                  >
                    <span>✓ Confirm & Save to Record</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Box 2: Medical Documents Attached */}
            <div className="border border-[#D9E2DF] rounded-2xl p-5 bg-white">
              <h3 className="text-sm font-bold uppercase tracking-wider text-[#243331] mb-3 flex items-center gap-2">
                <span>📎 Medical Documents & Scans</span>
                <span className="text-xs font-normal text-[#647471]">
                  ({selectedPatient.historySummary.uploadedDocuments.length})
                </span>
              </h3>

              {selectedPatient.historySummary.uploadedDocuments.length > 0 ? (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {selectedPatient.historySummary.uploadedDocuments.map((doc) => (
                    <div
                      key={doc.id}
                      className="p-3 bg-[#F6F8F7] border border-[#D9E2DF] rounded-xl flex items-center justify-between"
                    >
                      <div className="flex items-center gap-2.5">
                        <svg className="w-5 h-5 text-[#B85C5C]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                        </svg>
                        <div>
                          <p className="text-xs font-bold text-[#243331]">{doc.title}</p>
                          <p className="text-[10px] text-[#647471]">{doc.date} • {doc.size}</p>
                        </div>
                      </div>
                      <span className="text-[11px] font-semibold text-[#2563EB] cursor-pointer hover:underline">
                        Open PDF
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-[#647471] italic">
                  No physical documents scanned during intake.
                </p>
              )}
            </div>

            {/* Box 3: Longitudinal Timeline & Previous Visits */}
            <div className="border border-[#D9E2DF] rounded-2xl p-5 bg-white">
              <h3 className="text-sm font-bold uppercase tracking-wider text-[#243331] mb-3">
                📅 Patient Longitudinal Record
              </h3>
              {selectedPatient.previousVisits.length > 0 ? (
                <div className="space-y-3">
                  {selectedPatient.previousVisits.map((vis) => (
                    <div
                      key={vis.id}
                      className="p-3 bg-[#F6F8F7] border border-[#D9E2DF] rounded-xl flex items-center justify-between text-xs"
                    >
                      <div>
                        <span className="font-bold text-[#243331]">{vis.date}</span>
                        <span className="mx-2 text-[#D9E2DF]">|</span>
                        <span className="font-semibold text-[#2F7D73]">{vis.complaint}</span>
                      </div>
                      <span className="text-[#647471]">
                        {vis.doctor} ({vis.department})
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-xs text-[#647471] italic">
                  First visit recorded in MediKiosk system.
                </p>
              )}
            </div>
          </div>
        </section>
      </main>

      {/* Health Status Modal (Preserves backend verification) */}
      {showHealthModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-3xl p-6 max-w-lg w-full shadow-2xl border border-[#D9E2DF]">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-[#243331]">Backend System Diagnostics</h3>
              <button
                type="button"
                onClick={() => setShowHealthModal(false)}
                className="text-gray-400 hover:text-gray-600 text-lg font-bold"
              >
                ✕
              </button>
            </div>
            <HealthStatus />
          </div>
        </div>
      )}
    </div>
  )
}
