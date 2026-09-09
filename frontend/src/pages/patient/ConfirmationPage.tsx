import React from 'react'
import { useKiosk } from '../../context/KioskContext'
import { useInstructionPlayer } from '../../hooks/useInstructionPlayer'
import { HearAgainButton } from '../../components/patient/HearAgainButton'

export const ConfirmationPage: React.FC = () => {
  const { tokenNumber, resetKiosk, setAppMode } = useKiosk()

  const instruction = `Thank you! Your information has been recorded. Your token number is ${tokenNumber}. Please take a seat in the OPD waiting area until your number is called.`

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

  return (
    <div className="flex flex-col items-center justify-between min-h-[calc(100vh-140px)] max-w-2xl mx-auto px-4 py-6 text-center">
      {/* Top Green Checkmark Circle Badge */}
      <div className="w-18 h-18 rounded-full bg-[#EBF4EE] text-[#4F8A6D] flex items-center justify-center my-2 shadow-xs">
        <svg className="w-10 h-10 stroke-current stroke-2" fill="none" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
        </svg>
      </div>

      {/* Heading */}
      <div className="my-2">
        <h2 className="text-3xl sm:text-4xl font-bold text-[#243331] mb-1 tracking-tight">
          Thank You!
        </h2>
        <p className="text-base sm:text-lg text-[#647471] font-medium">
          Your information has been recorded.
        </p>
      </div>

      {/* What Happens Next Card */}
      <div className="w-full bg-[#FFFFFF] border border-[#D9E2DF] rounded-2xl p-5 sm:p-6 shadow-sm my-3 text-left">
        <h3 className="text-base font-bold text-[#243331] mb-3 uppercase tracking-wide">
          What happens next?
        </h3>
        <ol className="space-y-3 text-sm sm:text-base text-[#243331]">
          <li className="flex items-start gap-3">
            <span className="w-6 h-6 rounded-full bg-[#DCEDEA] text-[#2F7D73] font-bold text-xs flex items-center justify-center flex-shrink-0 mt-0.5">
              1
            </span>
            <span>Your details and documents will be reviewed by the doctor.</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="w-6 h-6 rounded-full bg-[#DCEDEA] text-[#2F7D73] font-bold text-xs flex items-center justify-center flex-shrink-0 mt-0.5">
              2
            </span>
            <span>You will be called on the OPD display screen when it's your turn.</span>
          </li>
          <li className="flex items-start gap-3">
            <span className="w-6 h-6 rounded-full bg-[#DCEDEA] text-[#2F7D73] font-bold text-xs flex items-center justify-center flex-shrink-0 mt-0.5">
              3
            </span>
            <span>You can wait comfortably in the OPD waiting area.</span>
          </li>
        </ol>
      </div>

      {/* Large Token Number Card (matching storyboard) */}
      <div className="w-full bg-[#FFFFFF] border-2 border-[#2F7D73] rounded-3xl p-6 shadow-md my-2 flex flex-col items-center">
        <div className="flex items-center gap-2 text-[#647471] text-xs uppercase font-bold tracking-widest mb-1">
          <svg className="w-4 h-4 text-[#2F7D73]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 5v2m0 4v2m0 4v2M5 5a2 2 0 00-2 2v3a2 2 0 110 4v3a2 2 0 002 2h14a2 2 0 002-2v-3a2 2 0 110-4V7a2 2 0 00-2-2H5z" />
          </svg>
          <span>Your Token Number</span>
        </div>
        <div className="text-4xl sm:text-5xl font-black text-[#243331] tracking-tight font-mono">
          {tokenNumber}
        </div>
      </div>

      {/* Action Buttons: Back to Home + Doctor Dashboard link */}
      <div className="w-full space-y-2 mt-2">
        <button
          type="button"
          onClick={resetKiosk}
          className="w-full py-4 px-6 rounded-2xl bg-[#4F8A6D] hover:bg-[#3E6E56] active:bg-[#335B47] text-white font-bold text-lg sm:text-xl flex items-center justify-center gap-2 shadow-md hover:shadow-lg transition-all cursor-pointer min-h-[56px]"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          <span>Back to Home</span>
        </button>

        {/* Demo Helper: Switch directly to Doctor View */}
        <button
          type="button"
          onClick={() => setAppMode('doctor')}
          className="w-full py-2.5 text-xs font-semibold text-[#2563EB] hover:underline"
        >
          👨‍⚕️ View Doctor Review Dashboard for Token {tokenNumber} →
        </button>
      </div>

      {/* Bottom: Hear Again Button */}
      <div className="w-full flex justify-center mt-3">
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
