import React from 'react'
import type { InstructionStatus } from '../../types'

interface HearAgainButtonProps {
  onHearAgain: () => void
  status: InstructionStatus
  currentRepetition: number
  totalRepetitions: number
  isPlaying: boolean
}

export const HearAgainButton: React.FC<HearAgainButtonProps> = ({
  onHearAgain,
  status,
  currentRepetition,
  totalRepetitions,
  isPlaying,
}) => {
  return (
    <div className="flex flex-col items-center justify-center my-2 select-none">
      {/* Audio Playback Status Badge (Non-intrusive indicator) */}
      <div className="mb-2 h-5 flex items-center gap-1.5 text-xs text-[#647471]">
        {isPlaying ? (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-[#EFF6FF] border border-[#BFDBFE] text-[#1D4ED8] font-medium animate-pulse">
            <span className="w-2 h-2 rounded-full bg-[#2563EB]" />
            {status === 'FINAL_REPETITION'
              ? `Spoken Instruction: Final (${currentRepetition}/${totalRepetitions})`
              : `Spoken Instruction (${currentRepetition}/${totalRepetitions})`}
          </span>
        ) : status === 'COMPLETED' ? (
          <span className="text-[#647471] text-xs">
            Instruction complete. Press below to replay.
          </span>
        ) : null}
      </div>

      {/* Large Blue Circular Speaker Button */}
      <button
        type="button"
        onClick={onHearAgain}
        aria-label="Hear instructions again"
        title="Hear instructions again"
        className={`w-14 h-14 sm:w-16 sm:h-16 rounded-full bg-[#2563EB] hover:bg-[#1D4ED8] active:bg-[#1E40AF] text-white flex items-center justify-center shadow-md hover:shadow-lg transition-all transform active:scale-95 cursor-pointer focus:ring-4 focus:ring-[#BFDBFE] ${
          isPlaying ? 'ring-4 ring-[#BFDBFE] scale-105' : ''
        }`}
      >
        {/* Speaker Volume High Icon */}
        <svg
          className="w-7 h-7 sm:w-8 sm:h-8"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2.2"
            d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"
          />
        </svg>
      </button>

      {/* Storyboard Subtitle text */}
      <span className="text-xs text-[#647471] font-medium mt-1.5">
        (Instruction will repeat on tap)
      </span>
    </div>
  )
}
