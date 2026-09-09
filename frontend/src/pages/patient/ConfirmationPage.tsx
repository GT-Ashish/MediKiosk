import React, { useState, useEffect } from 'react'
import { useKiosk } from '../../context/KioskContext'
import { useInstructionPlayer } from '../../hooks/useInstructionPlayer'
import { HearAgainButton } from '../../components/patient/HearAgainButton'

export const ConfirmationPage: React.FC = () => {
  const { tokenNumber, resetKiosk, t, isMuted, selectedLanguage } = useKiosk()
  const [secondsLeft, setSecondsLeft] = useState(120)

  const {
    status,
    currentRepetition,
    totalRepetitions,
    isPlaying,
    replay,
  } = useInstructionPlayer({
    instruction: t.page9_confirmation.instruction,
    repeatCount: 2,
    autoPlay: true,
    langCode: selectedLanguage.code,
    isMuted,
  })

  // 120-second automatic redirect to Home/Language page (Item 15)
  useEffect(() => {
    const timer = setInterval(() => {
      setSecondsLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer)
          resetKiosk()
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(timer)
  }, [resetKiosk])

  return (
    <div className="flex flex-col items-center justify-between h-full max-w-4xl w-full mx-auto px-6 py-1 text-center select-none">
      {/* Top Green Checkmark Circle Badge */}
      <div className="w-16 h-16 rounded-full bg-[#EBF4EE] text-[#4F8A6D] flex items-center justify-center my-1 shadow-xs">
        <svg className="w-10 h-10 stroke-current stroke-2" fill="none" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
        </svg>
      </div>

      {/* Heading - Desktop First */}
      <div className="my-1 max-w-2xl">
        <h2 className="text-3xl sm:text-4xl font-bold text-[#243331] mb-1 tracking-tight">
          {t.page9_confirmation.title}
        </h2>
        <p className="text-base sm:text-lg text-[#647471] font-medium">
          {t.page9_confirmation.subtitle}
        </p>
      </div>

      {/* Large Token Number Card (matching storyboard) */}
      <div className="w-full max-w-lg bg-[#FFFFFF] border-2 border-[#2F7D73] rounded-3xl p-4 shadow-md my-2 flex flex-col items-center">
        <div className="flex items-center gap-2 text-[#647471] text-xs uppercase font-bold tracking-widest mb-1">
          <svg className="w-4 h-4 text-[#2F7D73]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z" />
          </svg>
          <span>{t.page9_confirmation.tokenLabel}</span>
        </div>
        <div className="text-5xl sm:text-6xl font-black text-[#243331] tracking-tight font-mono">
          {tokenNumber}
        </div>
      </div>

      {/* What Happens Next Card */}
      <div className="w-full max-w-2xl bg-[#FFFFFF] border border-[#D9E2DF] rounded-3xl p-5 sm:p-6 shadow-sm my-2 text-left">
        <h3 className="text-base font-bold text-[#243331] mb-4 uppercase tracking-wide">
          {t.page9_confirmation.nextStepsTitle}
        </h3>
        <ol className="space-y-2.5 text-sm sm:text-base text-[#243331]">
          <li className="flex items-start gap-3">
            <span className="w-7 h-7 rounded-full bg-[#DCEDEA] text-[#2F7D73] font-bold text-xs flex items-center justify-center flex-shrink-0 mt-0.5">
              1
            </span>
            <span>{t.page9_confirmation.step1}</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="w-7 h-7 rounded-full bg-[#DCEDEA] text-[#2F7D73] font-bold text-xs flex items-center justify-center flex-shrink-0 mt-0.5">
              2
            </span>
            <span>{t.page9_confirmation.step2}</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="w-7 h-7 rounded-full bg-[#DCEDEA] text-[#2F7D73] font-bold text-xs flex items-center justify-center flex-shrink-0 mt-0.5">
              3
            </span>
            <span>{t.page9_confirmation.step3}</span>
          </li>
        </ol>
      </div>

      {/* Countdown Indicator & Action Buttons */}
      <div className="w-full max-w-md space-y-2.5 mt-1">
        {/* Visible 120s Countdown */}
        <div className="flex items-center justify-center gap-2 px-4 py-2 bg-[#F6F8F7] border border-[#D9E2DF] rounded-full text-xs font-semibold text-[#647471]">
          <span className="w-2 h-2 rounded-full bg-[#2F7D73] animate-pulse" />
          <span>
            {t.page9_confirmation.autoReturnMessage.replace('{seconds}', secondsLeft.toString())}
          </span>
        </div>

        {/* Manual Back to Home Button */}
        <button
          type="button"
          onClick={resetKiosk}
          className="w-full py-4 px-6 rounded-2xl bg-[#4F8A6D] hover:bg-[#3E6E56] active:bg-[#335B47] text-white font-bold text-lg sm:text-xl flex items-center justify-center gap-2 shadow-md hover:shadow-lg transition-all cursor-pointer min-h-[56px]"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          <span>{t.common.backToHome}</span>
        </button>
      </div>

      {/* Bottom: Hear Again Button */}
      <div className="w-full flex justify-center mt-2 border-t border-[#D9E2DF] pt-2">
        <HearAgainButton
          onHearAgain={replay}
          status={status}
          currentRepetition={currentRepetition}
          totalRepetitions={totalRepetitions}
          isPlaying={isPlaying}
        />
      </div>
    </div>
  )
}

