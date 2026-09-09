import React from 'react'
import type { VoiceListeningStatus } from '../../types'

interface VoiceWaveformProps {
  status: VoiceListeningStatus
  statusMessage: string
  transcript?: string
  onStartListening: () => void
  onManualSubmit?: (text: string) => void
  fallbackPlaceholder?: string
}

export const VoiceWaveform: React.FC<VoiceWaveformProps> = ({
  status,
  statusMessage,
  transcript,
  onStartListening,
  onManualSubmit,
  fallbackPlaceholder = 'Or type your answer here...',
}) => {
  const [manualText, setManualText] = React.useState('')
  const [isTyping, setIsTyping] = React.useState(false)

  const handleManualSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (manualText.trim() && onManualSubmit) {
      onManualSubmit(manualText.trim())
      setManualText('')
      setIsTyping(false)
    }
  }

  return (
    <div className="flex flex-col items-center justify-center my-4 w-full max-w-lg mx-auto">
      {/* Central Large Microphone Circle Button */}
      <div className="relative flex items-center justify-center my-3">
        {/* Animated Ripple Waves when listening */}
        {status === 'LISTENING' && (
          <div className="absolute w-28 h-28 rounded-full bg-[#2F7D73] opacity-20 animate-ping pointer-events-none" />
        )}
        {status === 'PROCESSING' && (
          <div className="absolute w-24 h-24 rounded-full border-4 border-[#2F7D73] border-t-transparent animate-spin pointer-events-none" />
        )}

        <button
          type="button"
          onClick={onStartListening}
          className={`w-20 h-20 sm:w-24 sm:h-24 rounded-full flex items-center justify-center shadow-lg transition-all transform active:scale-95 cursor-pointer ${
            status === 'SUCCESS'
              ? 'bg-[#4F8A6D] text-white'
              : status === 'RETRY'
              ? 'bg-[#B8874A] text-white'
              : 'bg-[#2F7D73] text-white'
          }`}
          aria-label="Microphone active"
        >
          {/* Microphone Icon */}
          <svg className="w-10 h-10 sm:w-11 sm:h-11" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2.2"
              d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
            />
          </svg>
        </button>
      </div>

      {/* Status Message: "I'm listening..." */}
      <h3 className="text-xl sm:text-2xl font-semibold text-[#243331] mt-2 mb-2">
        {statusMessage}
      </h3>

      {/* Animated Sound Waveform Bars */}
      {status === 'LISTENING' && (
        <div className="flex items-center gap-1.5 h-10 my-2">
          {[
            { height: '14px', delay: '0s' },
            { height: '26px', delay: '0.15s' },
            { height: '36px', delay: '0.3s' },
            { height: '22px', delay: '0.45s' },
            { height: '38px', delay: '0.2s' },
            { height: '18px', delay: '0.35s' },
            { height: '32px', delay: '0.1s' },
            { height: '16px', delay: '0.25s' },
          ].map((bar, i) => (
            <div
              key={i}
              className="w-1.5 bg-[#2F7D73] rounded-full"
              style={{
                height: bar.height,
                animation: `wave-bar 0.9s ease-in-out infinite alternate ${bar.delay}`,
              }}
            />
          ))}
        </div>
      )}

      {/* Captured Speech Output (when transcribed or in progress) */}
      {transcript && (
        <div className="w-full bg-[#FFFFFF] border-2 border-[#2F7D73] rounded-2xl p-4 my-3 shadow-sm text-center animate-fade-in">
          <p className="text-xs uppercase font-bold tracking-wider text-[#2F7D73] mb-1">
            Transcribed Speech
          </p>
          <p className="text-lg font-medium text-[#243331] italic">
            "{transcript}"
          </p>
        </div>
      )}

      {/* Typing / Touch Fallback Bar */}
      <div className="w-full mt-3">
        {isTyping ? (
          <form onSubmit={handleManualSubmit} className="flex gap-2">
            <input
              type="text"
              value={manualText}
              onChange={(e) => setManualText(e.target.value)}
              placeholder="Type your response here..."
              className="flex-1 px-4 py-3 bg-white border border-[#D9E2DF] rounded-xl text-base text-[#243331] focus:ring-2 focus:ring-[#2F7D73] focus:border-transparent outline-none shadow-sm"
              autoFocus
            />
            <button
              type="submit"
              className="px-5 py-3 bg-[#4F8A6D] hover:bg-[#3E6E56] text-white font-semibold rounded-xl text-sm transition-colors cursor-pointer"
            >
              Submit
            </button>
            <button
              type="button"
              onClick={() => setIsTyping(false)}
              className="px-3 py-3 border border-[#D9E2DF] text-[#647471] rounded-xl text-sm hover:bg-gray-50 cursor-pointer"
            >
              Cancel
            </button>
          </form>
        ) : (
          <button
            type="button"
            onClick={() => setIsTyping(true)}
            className="w-full py-3 px-4 rounded-xl border border-[#D9E2DF] bg-white hover:bg-gray-50 text-sm text-[#647471] flex items-center justify-center gap-2 transition-colors shadow-sm cursor-pointer"
          >
            {/* Keyboard Icon */}
            <svg className="w-4 h-4 text-[#647471]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            <span>{fallbackPlaceholder}</span>
          </button>
        )}
      </div>
    </div>
  )
}
