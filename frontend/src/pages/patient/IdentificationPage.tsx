import React, { useState } from 'react'
import { useKiosk } from '../../context/KioskContext'
import type { IdentificationMethod } from '../../types'
import { useInstructionPlayer } from '../../hooks/useInstructionPlayer'
import { HearAgainButton } from '../../components/patient/HearAgainButton'

export const IdentificationPage: React.FC = () => {
  const { setPatient, patient, goTo, goBack, t, isMuted, selectedLanguage } = useKiosk()
  const [activeModal, setActiveModal] = useState<IdentificationMethod | null>(null)

  const {
    status,
    currentRepetition,
    totalRepetitions,
    isPlaying,
    replay,
  } = useInstructionPlayer({
    instruction: t.page3_identification.instruction,
    repeatCount: 2,
    autoPlay: true,
    langCode: selectedLanguage.code,
    isMuted,
  })

  const handleSelectMethod = (method: IdentificationMethod) => {
    setActiveModal(method)
  }

  const handleConfirmIdentity = () => {
    if (activeModal) {
      setPatient({
        ...patient,
        idMethod: activeModal,
      })
    }
    setActiveModal(null)
    goTo('visit_reason')
  }

  return (
    <div className="flex flex-col items-center justify-between h-full max-w-4xl w-full mx-auto px-6 py-1 select-none">
      {/* Heading - Desktop First */}
      <div className="text-center my-2 max-w-2xl">
        <h2 className="text-3xl sm:text-4xl font-bold text-[#243331] mb-2 tracking-tight">
          {t.page3_identification.title}
        </h2>
        <p className="text-base sm:text-lg text-[#647471] font-medium">
          {t.page3_identification.subtitle}
        </p>
      </div>

      {/* 3 Large Option Cards */}
      <div className="w-full space-y-3 my-3">
        {/* Option 1: Aadhaar */}
        <button
          type="button"
          onClick={() => handleSelectMethod('aadhaar')}
          className="w-full flex items-center justify-between p-5 bg-[#FFFFFF] border-2 border-[#D9E2DF] hover:border-[#2F7D73] hover:bg-[#F9FBFA] active:bg-[#DCEDEA] rounded-3xl shadow-sm hover:shadow-md transition-all cursor-pointer group text-left"
        >
          <div className="flex items-center gap-5">
            <div className="w-16 h-16 rounded-2xl bg-[#E8F4F1] text-[#2F7D73] flex items-center justify-center flex-shrink-0 group-hover:scale-105 transition-transform shadow-xs">
              {/* Fingerprint / Biometric Icon */}
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 11c0 3.517-1.009 6.799-2.753 9.571m-3.44-2.04l.054-.09A13.916 13.916 0 008 11a4 4 0 118 0c0 1.017-.07 2.019-.203 3m-2.118 6.844A21.88 21.88 0 0015.171 17m3.839 1.132c.645-2.266.99-4.659.99-7.132A8 8 0 004 11m0 0a8.003 8.003 0 0115.357-2m1.523 9.38A18.01 18.01 0 0112 21" />
              </svg>
            </div>
            <div>
              <h3 className="text-xl sm:text-2xl font-bold text-[#243331]">
                {t.page3_identification.aadhaarTitle}
              </h3>
              <p className="text-sm sm:text-base text-[#647471] mt-0.5">
                {t.page3_identification.aadhaarDesc}
              </p>
            </div>
          </div>
          <svg className="w-6 h-6 text-[#647471] group-hover:text-[#2F7D73] group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M9 5l7 7-7 7" />
          </svg>
        </button>

        {/* Option 2: ABHA ID */}
        <button
          type="button"
          onClick={() => handleSelectMethod('abha')}
          className="w-full flex items-center justify-between p-5 bg-[#FFFFFF] border-2 border-[#D9E2DF] hover:border-[#2F7D73] hover:bg-[#F9FBFA] active:bg-[#DCEDEA] rounded-3xl shadow-sm hover:shadow-md transition-all cursor-pointer group text-left"
        >
          <div className="flex items-center gap-5">
            <div className="w-16 h-16 rounded-2xl bg-[#EFF6FF] text-[#2563EB] flex items-center justify-center flex-shrink-0 group-hover:scale-105 transition-transform shadow-xs">
              {/* ID Badge Icon */}
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2" />
              </svg>
            </div>
            <div>
              <h3 className="text-xl sm:text-2xl font-bold text-[#243331]">
                {t.page3_identification.abhaTitle}
              </h3>
              <p className="text-sm sm:text-base text-[#647471] mt-0.5">
                {t.page3_identification.abhaDesc}
              </p>
            </div>
          </div>
          <svg className="w-6 h-6 text-[#647471] group-hover:text-[#2F7D73] group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M9 5l7 7-7 7" />
          </svg>
        </button>

        {/* Option 3: Enter Manually */}
        <button
          type="button"
          onClick={() => handleSelectMethod('manual')}
          className="w-full flex items-center justify-between p-5 bg-[#FFFFFF] border-2 border-[#D9E2DF] hover:border-[#2F7D73] hover:bg-[#F9FBFA] active:bg-[#DCEDEA] rounded-3xl shadow-sm hover:shadow-md transition-all cursor-pointer group text-left"
        >
          <div className="flex items-center gap-5">
            <div className="w-16 h-16 rounded-2xl bg-[#F6F8F7] text-[#647471] flex items-center justify-center flex-shrink-0 group-hover:scale-105 transition-transform shadow-xs">
              {/* User / Form Icon */}
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <div>
              <h3 className="text-xl sm:text-2xl font-bold text-[#243331]">
                {t.page3_identification.manualTitle}
              </h3>
              <p className="text-sm sm:text-base text-[#647471] mt-0.5">
                {t.page3_identification.manualDesc}
              </p>
            </div>
          </div>
          <svg className="w-6 h-6 text-[#647471] group-hover:text-[#2F7D73] group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>

      {/* Bottom Bar: Back button + Blue Hear Again button */}
      <div className="w-full flex items-center justify-between mt-auto pt-3 border-t border-[#D9E2DF]">
        <button
          type="button"
          onClick={goBack}
          className="px-6 py-3.5 rounded-xl border border-[#D9E2DF] bg-white hover:bg-gray-50 text-base font-semibold text-[#243331] flex items-center gap-2 transition-colors cursor-pointer shadow-xs min-h-[48px]"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M15 19l-7-7 7-7" />
          </svg>
          <span>{t.common.back}</span>
        </button>

        <HearAgainButton
          onHearAgain={replay}
          status={status}
          currentRepetition={currentRepetition}
          totalRepetitions={totalRepetitions}
          isPlaying={isPlaying}
        />

        <div className="w-24 hidden sm:block" />
      </div>

      {/* Mock Identification Entry Modal (Safe Demo Simulation) */}
      {activeModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-3xl p-6 sm:p-8 max-w-md w-full shadow-2xl border border-[#D9E2DF]">
            <h3 className="text-2xl font-bold text-[#243331] mb-2">
              {activeModal === 'aadhaar' && t.page3_identification.modalTitleAadhaar}
              {activeModal === 'abha' && t.page3_identification.modalTitleAbha}
              {activeModal === 'manual' && t.page3_identification.modalTitleManual}
            </h3>
            <p className="text-sm text-[#647471] mb-4">
              {t.page3_identification.modalDemoNotice}
            </p>

            <div className="p-4 bg-[#F6F8F7] rounded-xl border border-[#D9E2DF] mb-5">
              <p className="text-xs font-semibold text-[#2F7D73] uppercase tracking-wider mb-1">
                {t.page3_identification.modalProfileTitle}
              </p>
              <p className="text-base font-bold text-[#243331]">Rahul Sharma</p>
              <p className="text-sm text-[#647471]">32 years • Male</p>
              <p className="text-xs text-[#647471] mt-1 font-mono">
                {activeModal === 'aadhaar' && 'Aadhaar: XXXX-XXXX-4821'}
                {activeModal === 'abha' && 'ABHA: 91-8271-4829-1029'}
                {activeModal === 'manual' && 'Phone: +91 98765 43210'}
              </p>
            </div>

            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => setActiveModal(null)}
                className="flex-1 py-3.5 border border-[#D9E2DF] text-[#647471] font-semibold rounded-xl text-base hover:bg-gray-50 cursor-pointer"
              >
                {t.common.cancel}
              </button>
              <button
                type="button"
                onClick={handleConfirmIdentity}
                className="flex-1 py-3.5 bg-[#4F8A6D] text-white font-bold rounded-xl text-base hover:bg-[#3E6E56] shadow-md cursor-pointer"
              >
                {t.common.confirm}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

