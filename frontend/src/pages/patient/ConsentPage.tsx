import React, { useState } from 'react'
import { useKiosk } from '../../context/KioskContext'
import { useInstructionPlayer } from '../../hooks/useInstructionPlayer'
import { HearAgainButton } from '../../components/patient/HearAgainButton'

export const ConsentPage: React.FC = () => {
  const { setConsentGiven, goTo, goBack } = useKiosk()
  const [showDeclineModal, setShowDeclineModal] = useState(false)

  const instruction =
    'Your privacy matters. Press the green button if you agree to share your answers, documents, and medical history with the doctor. Press the red button if you do not agree.'

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

  const handleAgree = () => {
    setConsentGiven(true)
    goTo('identification')
  }

  const handleDecline = () => {
    setConsentGiven(false)
    setShowDeclineModal(true)
  }

  return (
    <div className="flex flex-col items-center justify-between min-h-[calc(100vh-140px)] max-w-2xl mx-auto px-4 py-6">
      {/* Top Lock Icon Badge */}
      <div className="w-16 h-16 rounded-full bg-[#DCEDEA] text-[#2F7D73] flex items-center justify-center mb-3 shadow-xs">
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2.2"
            d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
          />
        </svg>
      </div>

      {/* Heading */}
      <div className="text-center mb-6">
        <h2 className="text-3xl sm:text-4xl font-bold text-[#243331] mb-2 tracking-tight">
          Your Privacy Matters
        </h2>
        <p className="text-base sm:text-lg text-[#647471] font-medium">
          We need your permission to continue. We may collect:
        </p>
      </div>

      {/* 3 Information Items (Card list matching storyboard) */}
      <div className="w-full bg-[#FFFFFF] border border-[#D9E2DF] rounded-2xl p-5 sm:p-6 shadow-sm mb-6 space-y-4">
        {/* Item 1: Mic */}
        <div className="flex items-center gap-4">
          <div className="w-11 h-11 rounded-xl bg-[#F6F8F7] text-[#2F7D73] flex items-center justify-center flex-shrink-0">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
            </svg>
          </div>
          <span className="text-lg sm:text-xl font-semibold text-[#243331]">
            Your answers (voice or text)
          </span>
        </div>

        <div className="h-px bg-[#EBF0EE]" />

        {/* Item 2: Document */}
        <div className="flex items-center gap-4">
          <div className="w-11 h-11 rounded-xl bg-[#F6F8F7] text-[#2F7D73] flex items-center justify-center flex-shrink-0">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <span className="text-lg sm:text-xl font-semibold text-[#243331]">
            Your medical documents
          </span>
        </div>

        <div className="h-px bg-[#EBF0EE]" />

        {/* Item 3: Clock */}
        <div className="flex items-center gap-4">
          <div className="w-11 h-11 rounded-xl bg-[#F6F8F7] text-[#2F7D73] flex items-center justify-center flex-shrink-0">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <span className="text-lg sm:text-xl font-semibold text-[#243331]">
            Your medical history
          </span>
        </div>
      </div>

      {/* Binary Decision Buttons (RED & GREEN as specified) */}
      <div className="grid grid-cols-2 gap-4 w-full mb-6">
        {/* Red: I Don't Agree */}
        <button
          type="button"
          onClick={handleDecline}
          className="py-4 px-6 rounded-2xl bg-[#B85C5C] hover:bg-[#9E4A4A] active:bg-[#853C3C] text-white font-bold text-lg sm:text-xl flex items-center justify-center gap-3 shadow-md hover:shadow-lg transition-all cursor-pointer min-h-[56px]"
        >
          <svg className="w-6 h-6 stroke-current stroke-2" fill="none" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
          <span>I Don't Agree</span>
        </button>

        {/* Green: I Agree */}
        <button
          type="button"
          onClick={handleAgree}
          className="py-4 px-6 rounded-2xl bg-[#4F8A6D] hover:bg-[#3E6E56] active:bg-[#335B47] text-white font-bold text-lg sm:text-xl flex items-center justify-center gap-3 shadow-md hover:shadow-lg transition-all cursor-pointer min-h-[56px]"
        >
          <svg className="w-6 h-6 stroke-current stroke-2" fill="none" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
          </svg>
          <span>I Agree</span>
        </button>
      </div>

      {/* Bottom Area: Hear Again Button */}
      <div className="w-full flex justify-center mt-auto">
        <HearAgainButton
          onHearAgain={replay}
          status={status}
          currentRepetition={currentRepetition}
          totalRepetitions={totalRepetitions}
          isPlaying={isPlaying}
        />
      </div>

      {/* Gentle Decline Modal */}
      {showDeclineModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-3xl p-6 sm:p-8 max-w-md w-full shadow-2xl border border-[#D9E2DF] text-center">
            <div className="w-14 h-14 rounded-full bg-[#F9EBEB] text-[#B85C5C] flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-[#243331] mb-2">Consent Required</h3>
            <p className="text-sm text-[#647471] mb-6">
              To prepare your clinical history and documents for your doctor, MediKiosk requires your permission. Your data is stored securely and deleted after your OPD visit.
            </p>
            <div className="flex flex-col gap-3">
              <button
                type="button"
                onClick={() => {
                  setShowDeclineModal(false)
                  handleAgree()
                }}
                className="w-full py-3.5 bg-[#4F8A6D] text-white font-bold rounded-xl text-base hover:bg-[#3E6E56] transition-colors"
              >
                I Understand, I Agree
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowDeclineModal(false)
                  goBack()
                }}
                className="w-full py-3 text-[#647471] font-medium text-sm hover:underline"
              >
                Return to Language Selection
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
