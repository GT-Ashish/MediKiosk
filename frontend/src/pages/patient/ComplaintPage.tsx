import React from 'react'
import { useKiosk } from '../../context/KioskContext'
import { useInstructionPlayer } from '../../hooks/useInstructionPlayer'
import { useVoiceInteraction } from '../../hooks/useVoiceInteraction'
import { HearAgainButton } from '../../components/patient/HearAgainButton'
import { VoiceWaveform } from '../../components/patient/VoiceWaveform'

export const ComplaintPage: React.FC = () => {
  const { setChiefComplaint, goTo, goBack } = useKiosk()

  const instruction =
    "Tell me about your problem. You can speak in your own words. You don't need to use medical terms."

  const {
    status: instructionStatus,
    currentRepetition,
    totalRepetitions,
    isPlaying: isInstructionPlaying,
    replay,
  } = useInstructionPlayer({
    instruction,
    repeatCount: 2,
    autoPlay: true,
  })

  // Automatic voice listening on mount
  const {
    status: voiceStatus,
    statusMessage,
    transcript,
    startListening,
    triggerManualSuccess,
  } = useVoiceInteraction({
    autoStart: true,
    defaultMockTranscript: 'I have had stomach pain for three days.',
    onSuccess: (text) => {
      setChiefComplaint(text)
    },
  })

  const handleNext = () => {
    if (transcript) {
      setChiefComplaint(transcript)
    }
    goTo('history_taking')
  }

  return (
    <div className="flex flex-col items-center justify-between min-h-[calc(100vh-140px)] max-w-2xl mx-auto px-4 py-6">
      {/* Heading */}
      <div className="text-center my-2">
        <h2 className="text-3xl sm:text-4xl font-bold text-[#243331] mb-2 tracking-tight">
          Tell me about your problem
        </h2>
        <p className="text-base sm:text-lg text-[#647471] font-medium">
          You can speak in your own words. You don't need to use medical terms.
        </p>
      </div>

      {/* Voice Interaction & Listening Area */}
      <div className="w-full my-auto">
        <VoiceWaveform
          status={voiceStatus}
          statusMessage={statusMessage}
          transcript={transcript}
          onStartListening={startListening}
          onManualSubmit={(manualText) => {
            triggerManualSuccess(manualText)
            setChiefComplaint(manualText)
          }}
          fallbackPlaceholder="Or type your answer here..."
        />

        {/* Continue Button appears once voice/input is transcribed */}
        {transcript && (
          <div className="flex justify-center mt-4 animate-fade-in">
            <button
              type="button"
              onClick={handleNext}
              className="px-8 py-4 bg-[#4F8A6D] hover:bg-[#3E6E56] active:bg-[#335B47] text-white font-bold text-lg rounded-2xl shadow-md hover:shadow-lg transition-all flex items-center gap-2 cursor-pointer min-h-[56px]"
            >
              <span>Continue to Next Question</span>
              <svg className="w-5 h-5 stroke-current stroke-2" fill="none" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </button>
          </div>
        )}
      </div>

      {/* Bottom Bar: Back + Hear Again */}
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
          status={instructionStatus}
          currentRepetition={currentRepetition}
          totalRepetitions={totalRepetitions}
          isPlaying={isInstructionPlaying}
        />

        <div className="w-20" /> {/* Balance spacer */}
      </div>
    </div>
  )
}
