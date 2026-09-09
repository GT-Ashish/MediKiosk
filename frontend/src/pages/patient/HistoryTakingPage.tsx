import React, { useState } from 'react'
import { useKiosk } from '../../context/KioskContext'
import { HISTORY_QUESTIONS } from '../../data/mockData'
import { useInstructionPlayer } from '../../hooks/useInstructionPlayer'
import { useVoiceInteraction } from '../../hooks/useVoiceInteraction'
import { HearAgainButton } from '../../components/patient/HearAgainButton'
import { VoiceWaveform } from '../../components/patient/VoiceWaveform'

export const HistoryTakingPage: React.FC = () => {
  const { setAnswerForQuestion, goTo, goBack } = useKiosk()
  const [questionIndex, setQuestionIndex] = useState(0)

  const currentQ = HISTORY_QUESTIONS[questionIndex]
  const totalQuestions = HISTORY_QUESTIONS.length

  const instruction = `${currentQ.title} You can answer by speaking or by tapping an option on the screen.`

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

  // Automatic voice listening for this question
  const {
    status: voiceStatus,
    statusMessage,
    transcript,
    startListening,
  } = useVoiceInteraction({
    autoStart: true,
    defaultMockTranscript: currentQ.defaultAnswer,
    onSuccess: (text) => {
      setAnswerForQuestion(currentQ.id, currentQ.title, text)
    },
  })

  const advanceQuestion = (chosenAnswer: string) => {
    setAnswerForQuestion(currentQ.id, currentQ.title, chosenAnswer)
    if (questionIndex + 1 < totalQuestions) {
      setQuestionIndex((prev) => prev + 1)
    } else {
      goTo('documents')
    }
  }

  const handleSkip = () => {
    advanceQuestion('Not sure / Skipped')
  }

  return (
    <div className="flex flex-col items-center justify-between min-h-[calc(100vh-140px)] max-w-2xl mx-auto px-4 py-6">
      {/* Question Counter & Heading */}
      <div className="text-center my-2">
        <span className="text-xs uppercase font-bold tracking-widest text-[#2F7D73] bg-[#DCEDEA] px-3 py-1 rounded-full">
          Question {questionIndex + 1} of {totalQuestions}
        </span>
        <h2 className="text-3xl sm:text-4xl font-bold text-[#243331] mt-2 mb-1 tracking-tight">
          {currentQ.title}
        </h2>
        <p className="text-base sm:text-lg text-[#647471] font-medium">
          {currentQ.subtitle}
        </p>
      </div>

      {/* Voice Listening Waveform Area */}
      <div className="w-full my-2">
        <VoiceWaveform
          status={voiceStatus}
          statusMessage={statusMessage}
          transcript={transcript}
          onStartListening={startListening}
          onManualSubmit={(text) => advanceQuestion(text)}
          fallbackPlaceholder="Or type custom response here..."
        />
      </div>

      {/* Touch Options Grid (Dual-mode input: Tap OR Speak) */}
      <div className="w-full my-3">
        <p className="text-xs font-bold uppercase tracking-wider text-[#647471] text-center mb-3">
          Or Tap an Option Below:
        </p>
        <div className="grid grid-cols-2 gap-3 w-full">
          {currentQ.options.map((opt) => (
            <button
              key={opt.id}
              type="button"
              onClick={() => advanceQuestion(opt.label)}
              className="py-4 px-5 bg-[#FFFFFF] border-2 border-[#D9E2DF] hover:border-[#2F7D73] hover:bg-[#F9FBFA] active:bg-[#DCEDEA] rounded-2xl text-base sm:text-lg font-bold text-[#243331] shadow-xs hover:shadow-sm transition-all cursor-pointer text-center min-h-[56px] flex items-center justify-center"
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {/* Bottom Bar: Back + Hear Again + Skip */}
      <div className="w-full flex items-center justify-between mt-auto pt-4 border-t border-[#D9E2DF]">
        <button
          type="button"
          onClick={() => {
            if (questionIndex > 0) {
              setQuestionIndex((prev) => prev - 1)
            } else {
              goBack()
            }
          }}
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

        <button
          type="button"
          onClick={handleSkip}
          className="px-4 py-2.5 rounded-xl text-sm font-semibold text-[#647471] hover:text-[#243331] hover:bg-gray-100 transition-colors cursor-pointer"
        >
          Skip (If not sure)
        </button>
      </div>
    </div>
  )
}
