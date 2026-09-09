import React from 'react'
import { useKiosk } from '../../context/KioskContext'
import { PREVIOUS_VISITS } from '../../data/mockData'
import type { PreviousVisitRecord } from '../../types'
import { useInstructionPlayer } from '../../hooks/useInstructionPlayer'
import { HearAgainButton } from '../../components/patient/HearAgainButton'

export const FollowUpPage: React.FC = () => {
  const {
    selectedPreviousVisit,
    setSelectedPreviousVisit,
    goTo,
    goBack,
  } = useKiosk()

  const instruction =
    'Select your previous visit. Choose the visit to which you want to add new reports, then press Next.'

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

  const handleSelectVisit = (visit: PreviousVisitRecord) => {
    setSelectedPreviousVisit(visit)
  }

  const handleNext = () => {
    goTo('documents')
  }

  return (
    <div className="flex flex-col items-center justify-between min-h-[calc(100vh-140px)] max-w-2xl mx-auto px-4 py-6">
      {/* Heading */}
      <div className="text-center my-3">
        <h2 className="text-3xl sm:text-4xl font-bold text-[#243331] mb-2 tracking-tight">
          Select your previous visit
        </h2>
        <p className="text-base sm:text-lg text-[#647471] font-medium">
          Choose the visit to which you want to add new reports.
        </p>
      </div>

      {/* List of Previous Visits (matching storyboard radio cards) */}
      <div className="w-full space-y-4 my-6">
        {PREVIOUS_VISITS.map((visit) => {
          const isSelected = selectedPreviousVisit?.id === visit.id

          return (
            <button
              key={visit.id}
              type="button"
              onClick={() => handleSelectVisit(visit)}
              className={`w-full flex items-center justify-between p-5 sm:p-6 rounded-2xl border-2 transition-all cursor-pointer text-left shadow-xs ${
                isSelected
                  ? 'bg-[#EBF4EE] border-[#4F8A6D] ring-2 ring-[#4F8A6D]/20'
                  : 'bg-[#FFFFFF] border-[#D9E2DF] hover:border-[#2F7D73] hover:bg-[#F9FBFA]'
              }`}
            >
              <div className="flex items-center gap-4">
                {/* Hospital Visit Icon */}
                <div
                  className={`w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0 ${
                    isSelected
                      ? 'bg-[#4F8A6D] text-white'
                      : 'bg-[#F6F8F7] text-[#647471]'
                  }`}
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>

                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-lg sm:text-xl font-bold text-[#243331]">
                      {visit.date}
                    </span>
                    <span className="text-xs font-semibold px-2 py-0.5 rounded bg-white text-[#647471] border border-[#D9E2DF]">
                      {visit.department}
                    </span>
                  </div>
                  <p className="text-base font-semibold text-[#2F7D73] mt-0.5">
                    {visit.complaint}
                  </p>
                  <p className="text-xs text-[#647471] mt-0.5">
                    Consulting Doctor: {visit.doctor}
                  </p>
                </div>
              </div>

              {/* Radio Indicator (Green checkmark circle when selected) */}
              <div
                className={`w-7 h-7 rounded-full flex items-center justify-center border-2 transition-all ${
                  isSelected
                    ? 'bg-[#4F8A6D] border-[#4F8A6D] text-white'
                    : 'border-[#D9E2DF] bg-white'
                }`}
              >
                {isSelected && (
                  <svg className="w-4 h-4 stroke-current stroke-3" fill="none" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                )}
              </div>
            </button>
          )
        })}
      </div>

      {/* Bottom Bar: Back + Hear Again + Next */}
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
          onClick={handleNext}
          className="px-7 py-3 bg-[#4F8A6D] hover:bg-[#3E6E56] active:bg-[#335B47] text-white font-bold text-base rounded-xl shadow-md flex items-center gap-2 transition-all cursor-pointer min-h-[48px]"
        >
          <span>Next</span>
          <svg className="w-5 h-5 stroke-current stroke-2" fill="none" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
          </svg>
        </button>
      </div>
    </div>
  )
}
