import React, { useState } from 'react'
import { useKiosk } from '../../context/KioskContext'
import { useInstructionPlayer } from '../../hooks/useInstructionPlayer'
import { HearAgainButton } from '../../components/patient/HearAgainButton'

export const ReviewSummaryPage: React.FC = () => {
  const {
    patient,
    visitType,
    chiefComplaint,
    historyAnswers,
    documents,
    goTo,
    goBack,
  } = useKiosk()

  const [editSection, setEditSection] = useState<'info' | 'points' | null>(null)
  const [editedComplaint, setEditedComplaint] = useState(chiefComplaint)
  const [viewingDoc, setViewingDoc] = useState<string | null>(null)

  const instruction =
    'Here is what we understood from your visit. Please review the details. You can tap Edit to modify any point, or press Looks Correct to confirm.'

  const {
    status,
    currentRepetition,
    totalRepetitions,
    isPlaying,
    replay,
  } = useInstructionPlayer({
    instruction,
    repeatCount: 2,
    autoPlay: true,
  })

  // Dynamic summary key points derived from history answers
  const keyPoints = [
    `Chief complaint: ${chiefComplaint}`,
    `Onset: ${historyAnswers.onset || 'Few days ago (3 days)'}`,
    `Location: ${historyAnswers.location || 'Lower abdominal region'}`,
    `Severity: ${historyAnswers.severity || 'Moderate severity'}`,
    `Associated: ${historyAnswers.associated || 'No vomiting, mild loss of appetite'}`,
    'No known drug allergies reported',
  ]

  return (
    <div className="flex flex-col items-center justify-between min-h-[calc(100vh-140px)] max-w-2xl mx-auto px-4 py-6">
      {/* Heading */}
      <div className="text-center my-2">
        <h2 className="text-3xl sm:text-4xl font-bold text-[#243331] mb-2 tracking-tight">
          Here's what we understood
        </h2>
        <p className="text-base sm:text-lg text-[#647471] font-medium">
          Please review and confirm.
        </p>
      </div>

      {/* Main Review Summary Card (matching storyboard) */}
      <div className="w-full bg-[#FFFFFF] border border-[#D9E2DF] rounded-3xl p-5 sm:p-7 shadow-sm my-4 space-y-6">
        {/* Section 1: Your Information */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-bold text-[#243331] flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[#2F7D73]" />
              Your Information
            </h3>
            <button
              type="button"
              onClick={() => setEditSection('info')}
              className="text-xs font-semibold text-[#2F7D73] hover:text-[#276B63] bg-[#DCEDEA] px-2.5 py-1 rounded-lg flex items-center gap-1 cursor-pointer"
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
              </svg>
              <span>Edit</span>
            </button>
          </div>

          <dl className="grid grid-cols-2 gap-y-2 text-sm sm:text-base bg-[#F6F8F7] p-3.5 rounded-2xl border border-[#EBF0EE]">
            <dt className="text-[#647471]">Name</dt>
            <dd className="font-bold text-[#243331]">{patient.name}</dd>

            <dt className="text-[#647471]">Age / Gender</dt>
            <dd className="font-semibold text-[#243331]">{patient.age} years / {patient.gender}</dd>

            <dt className="text-[#647471]">Visit Type</dt>
            <dd className="font-semibold text-[#2F7D73]">
              {visitType === 'new_problem' ? 'New Problem' : 'Follow-up Visit'}
            </dd>

            <dt className="text-[#647471]">Chief Complaint</dt>
            <dd className="font-semibold text-[#243331]">{chiefComplaint}</dd>
          </dl>
        </div>

        {/* Section 2: Key Points from Conversation */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-bold text-[#243331] flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[#2F7D73]" />
              Key Points from Conversation
            </h3>
            <button
              type="button"
              onClick={() => setEditSection('points')}
              className="text-xs font-semibold text-[#2F7D73] hover:text-[#276B63] bg-[#DCEDEA] px-2.5 py-1 rounded-lg flex items-center gap-1 cursor-pointer"
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
              </svg>
              <span>Edit</span>
            </button>
          </div>

          <ul className="space-y-2 text-sm sm:text-base text-[#243331] bg-[#F6F8F7] p-3.5 rounded-2xl border border-[#EBF0EE]">
            {keyPoints.map((pt, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="text-[#2F7D73] font-bold">•</span>
                <span>{pt}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Section 3: Uploaded Documents */}
        <div>
          <h3 className="text-lg font-bold text-[#243331] mb-3 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#2F7D73]" />
            Uploaded Documents ({documents.length})
          </h3>
          {documents.length > 0 ? (
            <div className="space-y-2">
              {documents.map((doc) => (
                <div
                  key={doc.id}
                  className="flex items-center justify-between p-3 bg-[#F6F8F7] rounded-xl border border-[#EBF0EE]"
                >
                  <div className="flex items-center gap-2.5">
                    <svg className="w-5 h-5 text-[#B85C5C]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                    <span className="text-sm font-semibold text-[#243331]">{doc.title}</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => setViewingDoc(doc.title)}
                    className="text-xs font-semibold text-[#2563EB] hover:underline cursor-pointer"
                  >
                    👁 View
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-[#647471] italic">No prior documents attached for this visit.</p>
          )}
        </div>

        {/* Clinical Safety Draft Disclaimer */}
        <div className="p-3 bg-[#EFF6FF] border border-[#BFDBFE] rounded-xl text-xs text-[#1D4ED8]">
          <span className="font-bold">Notice:</span> This structured summary is a draft prepared for your physician to review and edit during your consultation. It does not constitute a clinical diagnosis.
        </div>
      </div>

      {/* Bottom Bar: Back + Hear Again + Looks Correct */}
      <div className="w-full flex items-center justify-between mt-auto pt-4 border-t border-[#D9E2DF]">
        <button
          type="button"
          onClick={goBack}
          className="px-5 py-3 rounded-xl border border-[#D9E2DF] bg-white hover:bg-gray-50 text-base font-semibold text-[#243331] flex items-center gap-2 transition-colors cursor-pointer shadow-xs min-h-[48px]"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M15 19l-7-7 7-7" />
          </svg>
          <span>Back</span>
        </button>

        <HearAgainButton
          onHearAgain={replay}
          status={status}
          currentRepetition={currentRepetition}
          totalRepetitions={totalRepetitions}
          isPlaying={isPlaying}
        />

        <button
          type="button"
          onClick={() => goTo('confirmation')}
          className="px-7 py-3 bg-[#4F8A6D] hover:bg-[#3E6E56] active:bg-[#335B47] text-white font-bold text-base rounded-xl shadow-md flex items-center gap-2 transition-all cursor-pointer min-h-[48px]"
        >
          <span>Looks Correct</span>
          <svg className="w-5 h-5 stroke-current stroke-2" fill="none" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
          </svg>
        </button>
      </div>

      {/* Quick Edit Modal */}
      {editSection && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-3xl p-6 max-w-md w-full shadow-2xl border border-[#D9E2DF]">
            <h3 className="text-xl font-bold text-[#243331] mb-3">
              Edit {editSection === 'info' ? 'Chief Complaint' : 'History Details'}
            </h3>
            <textarea
              value={editedComplaint}
              onChange={(e) => setEditedComplaint(e.target.value)}
              className="w-full h-28 p-3 border border-[#D9E2DF] rounded-xl text-base text-[#243331] outline-none focus:ring-2 focus:ring-[#2F7D73] mb-4"
            />
            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => setEditSection(null)}
                className="flex-1 py-3 border border-[#D9E2DF] text-[#647471] font-semibold rounded-xl"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={() => setEditSection(null)}
                className="flex-1 py-3 bg-[#4F8A6D] text-white font-bold rounded-xl"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Document Preview Modal */}
      {viewingDoc && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-3xl p-6 max-w-md w-full shadow-2xl border border-[#D9E2DF] text-center">
            <div className="w-12 h-12 rounded-xl bg-[#DCEDEA] text-[#2F7D73] flex items-center justify-center mx-auto mb-3">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-bold text-[#243331] mb-1">{viewingDoc}</h3>
            <p className="text-xs text-[#647471] mb-4">Mock Document Preview • Verified by MediKiosk</p>
            <div className="h-40 bg-[#F6F8F7] border border-[#D9E2DF] rounded-xl flex items-center justify-center text-xs text-[#647471] mb-4 p-4">
              [Simulated Document Content: CBC & Metabolic Profile Within Normal Limits]
            </div>
            <button
              type="button"
              onClick={() => setViewingDoc(null)}
              className="w-full py-3 bg-[#2F7D73] text-white font-bold rounded-xl text-sm"
            >
              Close Preview
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
