import React, { useState, useEffect } from 'react'
import { useKiosk } from '../../context/KioskContext'
import type { PageRoute } from '../../types'

interface KioskHeaderProps {
  currentStep?: number
  totalSteps?: number
}

// Map routes to step numbers (1 to 6 main milestones)
const ROUTE_STEP_MAP: Record<PageRoute, number> = {
  language: 1,
  consent: 2,
  identification: 3,
  visit_reason: 4,
  complaint: 5,
  history_taking: 5,
  documents: 6,
  review: 7,
  confirmation: 8,
  follow_up: 5,
}

export const KioskHeader: React.FC<KioskHeaderProps> = () => {
  const { currentRoute, resetKiosk, t } = useKiosk()
  const [currentTime, setCurrentTime] = useState<string>('')
  const [currentDate, setCurrentDate] = useState<string>('')

  useEffect(() => {
    const updateTime = () => {
      const now = new Date()
      setCurrentTime(
        now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true })
      )
      setCurrentDate(
        now.toLocaleDateString('en-US', {
          weekday: 'short',
          day: 'numeric',
          month: 'short',
          year: 'numeric',
        })
      )
    }

    updateTime()
    const timer = setInterval(updateTime, 1000)
    return () => clearInterval(timer)
  }, [])

  const currentStep = ROUTE_STEP_MAP[currentRoute] || 1
  const totalSteps = 7

  return (
    <header className="w-full bg-[#FFFFFF] border-b border-[#D9E2DF] px-6 py-4 select-none">
      <div className="max-w-5xl mx-auto">
        {/* Top Branding & Meta Bar */}
        <div className="flex items-center justify-between">
          {/* Logo & Slogan */}
          <div
            onClick={resetKiosk}
            className="flex items-center gap-3 cursor-pointer group"
            title="Return to start"
          >
            <div className="w-10 h-10 rounded-xl bg-[#2F7D73] text-white flex items-center justify-center shadow-sm">
              {/* Medical Heart / Cross Icon */}
              <svg className="w-6 h-6 fill-current" viewBox="0 0 24 24">
                <path d="M19 10.5h-4.5V6a1.5 1.5 0 00-3 0v4.5H7a1.5 1.5 0 000 3h4.5V18a1.5 1.5 0 003 0v-4.5H19a1.5 1.5 0 00-3z" />
              </svg>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold tracking-tight text-[#243331]">
                  {t.header.brandName}
                </h1>
                <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded bg-[#DCEDEA] text-[#2F7D73]">
                  Kiosk
                </span>
              </div>
              <p className="text-xs text-[#647471] font-medium">
                {t.header.tagline}
              </p>
            </div>
          </div>

          {/* Time & Date */}
          <div className="flex items-center gap-4">
            <div className="text-right hidden sm:block">
              <div className="text-sm font-semibold text-[#243331]">{currentTime || '10:24 AM'}</div>
              <div className="text-xs text-[#647471]">{currentDate || 'Tue, 9 Sep 2026'}</div>
            </div>
          </div>
        </div>

        {/* Progress Step Indicator (as shown in storyboard) */}
        {currentRoute !== 'confirmation' && (
          <div className="mt-4 pt-3 border-t border-[#F1F5F4] flex items-center justify-center">
            <div className="flex items-center gap-2 sm:gap-3">
              {Array.from({ length: totalSteps }).map((_, index) => {
                const stepNum = index + 1
                const isCompleted = stepNum < currentStep
                const isCurrent = stepNum === currentStep

                return (
                  <React.Fragment key={stepNum}>
                    {/* Circle Dot */}
                    <div
                      className={`w-3.5 h-3.5 rounded-full transition-all duration-300 flex items-center justify-center ${
                        isCurrent
                          ? 'bg-[#2F7D73] ring-4 ring-[#DCEDEA] scale-110'
                          : isCompleted
                          ? 'bg-[#2F7D73]'
                          : 'bg-[#D9E2DF]'
                      }`}
                    >
                      {isCompleted && (
                        <div className="w-1.5 h-1.5 bg-white rounded-full" />
                      )}
                    </div>

                    {/* Connecting line between dots */}
                    {stepNum < totalSteps && (
                      <div
                        className={`w-5 sm:w-8 h-0.5 rounded transition-all duration-300 ${
                          stepNum < currentStep ? 'bg-[#2F7D73]' : 'bg-[#D9E2DF]'
                        }`}
                      />
                    )}
                  </React.Fragment>
                )
              })}
            </div>
          </div>
        )}
      </div>
    </header>
  )
}
