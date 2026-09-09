import React from 'react'
import { useKiosk } from '../../context/KioskContext'
import { SUPPORTED_LANGUAGES } from '../../data/mockData'
import type { SupportedLanguage } from '../../types'
import { useInstructionPlayer } from '../../hooks/useInstructionPlayer'
import { HearAgainButton } from '../../components/patient/HearAgainButton'

export const LanguagePage: React.FC = () => {
  const { setSelectedLanguage, goTo, t, isMuted, selectedLanguage } = useKiosk()

  // Instruction audio player: 2 repetitions, final includes reminder
  const {
    status,
    currentRepetition,
    totalRepetitions,
    isPlaying,
    replay,
  } = useInstructionPlayer({
    instruction: t.page1_language.instruction,
    repeatCount: 2,
    autoPlay: true,
    langCode: selectedLanguage.code,
    isMuted,
  })

  const handleSelectLanguage = (lang: SupportedLanguage) => {
    setSelectedLanguage(lang)
    goTo('consent')
  }

  return (
    <div className="flex flex-col items-center justify-between min-h-[calc(100vh-140px)] max-w-4xl w-full mx-auto px-6 py-8 select-none">
      {/* Page Heading - Desktop First */}
      <div className="text-center my-4 max-w-2xl">
        <h2 className="text-3xl sm:text-4xl font-bold text-[#243331] mb-2 tracking-tight">
          {t.page1_language.title}
        </h2>
        <p className="text-lg sm:text-xl text-[#647471] font-medium">
          {t.page1_language.subtitle}
        </p>
      </div>

      {/* Language Selection Grid (Desktop-First 4 Cards) */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-5 w-full my-6">
        {SUPPORTED_LANGUAGES.map((lang) => (
          <button
            key={lang.code}
            type="button"
            onClick={() => handleSelectLanguage(lang)}
            className="flex flex-col items-center justify-center p-6 bg-[#FFFFFF] border-2 border-[#D9E2DF] hover:border-[#2F7D73] hover:bg-[#F9FBFA] active:bg-[#DCEDEA] rounded-3xl shadow-sm hover:shadow-md transition-all duration-200 transform active:scale-98 min-h-[170px] cursor-pointer group"
          >
            {/* Circular Badge with native glyph */}
            <div
              className="w-16 h-16 rounded-2xl flex items-center justify-center text-2xl font-bold mb-3 transition-transform group-hover:scale-105 shadow-xs"
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
      <div className="w-full flex justify-center mt-auto pt-4 border-t border-[#D9E2DF]">
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

