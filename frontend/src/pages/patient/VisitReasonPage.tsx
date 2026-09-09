import React from 'react'
import { useKiosk } from '../../context/KioskContext'
import type { VisitType } from '../../types'
import { useInstructionPlayer } from '../../hooks/useInstructionPlayer'
import { HearAgainButton } from '../../components/patient/HearAgainButton'

export const VisitReasonPage: React.FC = () => {
  const { setVisitType, goTo, goBack, t, isMuted, selectedLanguage } = useKiosk()

  const {
    status,
    currentRepetition,
    totalRepetitions,
    isPlaying,
    replay,
  } = useInstructionPlayer({
    instruction: t.page4_visitReason.instruction,
    repeatCount: 2,
    autoPlay: true,
    langCode: selectedLanguage.code,
    isMuted,
  })

  const handleSelectReason = (type: VisitType) => {
    setVisitType(type)
    if (type === 'new_problem') {
      goTo('complaint') // Branch A: Chief complaint
    } else {
      goTo('follow_up') // Branch B: Select previous visit
    }
  }

  return (
    <div className="flex flex-col items-center justify-between min-h-[calc(100vh-140px)] max-w-4xl w-full mx-auto px-6 py-6 select-none">
      {/* Heading - Desktop First */}
      <div className="text-center my-4 max-w-2xl">
        <h2 className="text-3xl sm:text-4xl font-bold text-[#243331] mb-2 tracking-tight">
          {t.page4_visitReason.title}
        </h2>
        <p className="text-base sm:text-lg text-[#647471] font-medium">
          {t.page4_visitReason.subtitle}
        </p>
      </div>

      {/* Two Major Choice Cards (Desktop-First 2-Column Grid) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 w-full my-6">
        {/* OPTION 1: New Health Problem (Branch A) */}
        <button
          type="button"
          onClick={() => handleSelectReason('new_problem')}
          className="flex flex-col items-center text-center p-8 bg-[#FFFFFF] border-2 border-[#D9E2DF] hover:border-[#2F7D73] hover:bg-[#F9FBFA] active:bg-[#DCEDEA] rounded-3xl shadow-sm hover:shadow-md transition-all duration-200 cursor-pointer group justify-between min-h-[280px]"
        >
          <div className="flex flex-col items-center">
            {/* Stethoscope Icon in soft teal container */}
            <div className="w-20 h-20 rounded-2xl bg-[#DCEDEA] text-[#2F7D73] flex items-center justify-center mb-4 group-hover:scale-105 transition-transform shadow-xs">
              <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 8a4 4 0 01-8 0v4a4 4 0 004 4h0a4 4 0 004-4V8z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 16v3a2 2 0 01-2 2H8a2 2 0 01-2-2v-1" />
                <circle cx="6" cy="18" r="2" fill="currentColor" />
              </svg>
            </div>

            <h3 className="text-2xl font-bold text-[#243331] mb-2">
              {t.page4_visitReason.newProblemTitle}
            </h3>
            <p className="text-sm sm:text-base text-[#647471]">
              {t.page4_visitReason.newProblemDesc}
            </p>
          </div>

          {/* Forward Arrow Circle (Green as in storyboard) */}
          <div className="w-12 h-12 rounded-full bg-[#4F8A6D] text-white flex items-center justify-center mt-6 group-hover:scale-110 shadow-sm transition-transform">
            <svg className="w-6 h-6 stroke-current stroke-2" fill="none" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </div>
        </button>

        {/* OPTION 2: Follow-up Visit (Branch B) */}
        <button
          type="button"
          onClick={() => handleSelectReason('follow_up')}
          className="flex flex-col items-center text-center p-8 bg-[#FFFFFF] border-2 border-[#D9E2DF] hover:border-[#2563EB] hover:bg-[#F9FBFA] active:bg-[#EFF6FF] rounded-3xl shadow-sm hover:shadow-md transition-all duration-200 cursor-pointer group justify-between min-h-[280px]"
        >
          <div className="flex flex-col items-center">
            {/* Document / Reports Icon in soft blue container */}
            <div className="w-20 h-20 rounded-2xl bg-[#EFF6FF] text-[#2563EB] flex items-center justify-center mb-4 group-hover:scale-105 transition-transform shadow-xs">
              <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>

            <h3 className="text-2xl font-bold text-[#243331] mb-2">
              {t.page4_visitReason.followUpTitle}
            </h3>
            <p className="text-sm sm:text-base text-[#647471]">
              {t.page4_visitReason.followUpDesc}
            </p>
          </div>

          {/* Forward Arrow Circle (Blue as in storyboard) */}
          <div className="w-12 h-12 rounded-full bg-[#2563EB] text-white flex items-center justify-center mt-6 group-hover:scale-110 shadow-sm transition-transform">
            <svg className="w-6 h-6 stroke-current stroke-2" fill="none" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </div>
        </button>
      </div>

      {/* Bottom Bar: Back + Hear Again */}
      <div className="w-full flex items-center justify-between mt-auto pt-4 border-t border-[#D9E2DF]">
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
    </div>
  )
}

