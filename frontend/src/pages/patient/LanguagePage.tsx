import React from 'react'
import { useKiosk } from '../../context/KioskContext'
import { SUPPORTED_LANGUAGES } from '../../data/mockData'
import type { SupportedLanguage } from '../../types'
import { useInstructionPlayer } from '../../hooks/useInstructionPlayer'
import { HearAgainButton } from '../../components/patient/HearAgainButton'

export const LanguagePage: React.FC = () => {
  const { setSelectedLanguage, goTo } = useKiosk()

  // Instruction audio player: 2 repetitions, final includes reminder
  const instruction = 'Welcome to MediKiosk. Please choose your preferred language.'
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

  const handleSelectLanguage = (lang: SupportedLanguage) => {
    setSelectedLanguage(lang)
    goTo('consent')
  }

  return (
    <div className="flex flex-col items-center justify-between min-h-[calc(100vh-140px)] max-w-2xl mx-auto px-4 py-8">
      {/* Page Heading */}
      <div className="text-center my-4">
        <h2 className="text-3xl sm:text-4xl font-bold text-[#243331] mb-2 tracking-tight">
          Welcome to MediKiosk
        </h2>
        <p className="text-lg sm:text-xl text-[#647471] font-medium">
          Choose your preferred language
        </p>
      </div>

      {/* Language Selection Grid (2x2) */}
      <div className="grid grid-cols-2 gap-4 sm:gap-6 w-full my-6">
        {SUPPORTED_LANGUAGES.map((lang) => (
          <button
            key={lang.code}
            type="button"
            onClick={() => handleSelectLanguage(lang)}
            className="flex flex-col items-center justify-center p-6 sm:p-8 bg-[#FFFFFF] border-2 border-[#D9E2DF] hover:border-[#2F7D73] hover:bg-[#F9FBFA] active:bg-[#DCEDEA] rounded-2xl shadow-sm hover:shadow-md transition-all duration-200 transform active:scale-98 min-h-[140px] sm:min-h-[160px] cursor-pointer group"
          >
            {/* Circular Badge with native glyph */}
            <div
              className="w-14 h-14 rounded-full flex items-center justify-center text-xl font-bold mb-3 transition-transform group-hover:scale-110 shadow-xs"
              style={{ backgroundColor: lang.badgeBg, color: lang.badgeTextColor }}
            >
              {lang.badgeText}
            </div>

            {/* Language Names */}
            <span className="text-xl sm:text-2xl font-bold text-[#243331]">
              {lang.nativeName}
            </span>
            {lang.name !== lang.nativeName && (
              <span className="text-sm font-medium text-[#647471] mt-0.5">
                {lang.name}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Bottom Area: Persistent Blue Hear Again Speaker Button */}
      <div className="w-full flex justify-center mt-auto pt-4">
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
