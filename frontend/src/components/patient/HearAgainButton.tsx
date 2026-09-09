import React from 'react'
import type { InstructionStatus } from '../../types'
import { useKiosk } from '../../context/KioskContext'

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
  const { t, isMuted, toggleMute } = useKiosk()

  return (
    <div className="flex flex-col items-center justify-center my-3 select-none">
      {/* Audio Playback Status Badge (Non-intrusive indicator) */}
      <div className="mb-2 h-6 flex items-center justify-center text-xs text-[#647471]">
        {isMuted ? (
          <span className="inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full bg-[#F6F8F7] border border-[#D9E2DF] text-[#647471] font-medium">
            <span className="w-2 h-2 rounded-full bg-[#647471]" />
            Audio Muted
          </span>
        ) : isPlaying ? (
          <span className="inline-flex items-center gap-1.5 px-3 py-0.5 rounded-full bg-[#EFF6FF] border border-[#BFDBFE] text-[#1D4ED8] font-medium animate-pulse">
            <span className="w-2 h-2 rounded-full bg-[#2563EB]" />
            {status === 'FINAL_REPETITION'
              ? `Spoken Instruction: Final (${currentRepetition}/${totalRepetitions})`
              : `Spoken Instruction (${currentRepetition}/${totalRepetitions})`}
          </span>
        ) : status === 'COMPLETED' ? (
          <span className="text-[#647471] text-xs font-medium">
            Instruction complete. Press below to replay.
          </span>
        ) : null}
      </div>

      {/* Button Controls: [ 🔵 Hear Again ] [ 🔇 Mute / 🔊 Unmute ] */}
      <div className="flex items-center gap-3">
        {/* Blue Hear Again Button */}
        <button
          type="button"
          onClick={onHearAgain}
          aria-label="Hear instructions again"
          title="Hear instructions again"
          className={`px-5 py-3 rounded-2xl bg-[#2563EB] hover:bg-[#1D4ED8] active:bg-[#1E40AF] text-white font-bold text-sm sm:text-base flex items-center gap-2.5 shadow-md hover:shadow-lg transition-all transform active:scale-95 cursor-pointer focus:ring-4 focus:ring-[#BFDBFE] ${
            isPlaying ? 'ring-4 ring-[#BFDBFE] scale-102' : ''
          }`}
        >
          {/* Speaker Volume High Icon */}
          <svg className="w-5 h-5 sm:w-6 sm:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2.2"
              d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z"
            />
          </svg>
          <span>{t.common.hearAgain}</span>
        </button>

        {/* Mute / Unmute Toggle Button */}
        <button
          type="button"
          onClick={toggleMute}
          aria-label={isMuted ? 'Unmute instructions' : 'Mute instructions'}
          title={isMuted ? 'Unmute instructions' : 'Mute instructions'}
          className={`px-4 py-3 rounded-2xl border font-semibold text-sm flex items-center gap-2 shadow-xs transition-all cursor-pointer ${
            isMuted
              ? 'bg-[#F9EBEB] border-[#B85C5C] text-[#B85C5C] hover:bg-[#F3DCDC]'
              : 'bg-white border-[#D9E2DF] text-[#647471] hover:bg-gray-50 hover:text-[#243331]'
          }`}
        >
          {isMuted ? (
            <>
              {/* Speaker Off / Muted Icon */}
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" />
              </svg>
              <span>{t.common.unmute}</span>
            </>
          ) : (
            <>
              {/* Speaker Mute Icon */}
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M16 10l4 4m0-4l-4 4" />
              </svg>
              <span>{t.common.mute}</span>
            </>
          )}
        </button>
      </div>
    </div>
  )
}
