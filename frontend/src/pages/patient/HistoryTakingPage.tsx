import React, { useState, useRef, useEffect, useCallback } from 'react'
import { useKiosk } from '../../context/KioskContext'
import { useInstructionPlayer } from '../../hooks/useInstructionPlayer'
import { HearAgainButton } from '../../components/patient/HearAgainButton'
import {
  startSpeechRecognition,
  stopSpeaking,
  type SpeechRecognitionControls,
} from '../../utils/speech'

type QuestionKey = 'onset' | 'location' | 'severity' | 'associated'

const QUESTION_KEYS: QuestionKey[] = ['onset', 'location', 'severity', 'associated']

export const HistoryTakingPage: React.FC = () => {
  const {
    t,
    selectedLanguage,
    isMuted,
    setAnswerForQuestion,
    historyAnswers,
    goTo,
    goBack,
  } = useKiosk()

  const [questionIndex, setQuestionIndex] = useState(0)
  const currentKey = QUESTION_KEYS[questionIndex]
  const questionData = t.page6_history.questions[currentKey]

  const [isListening, setIsListening] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [liveTranscript, setLiveTranscript] = useState('')
  const [currentAnswer, setCurrentAnswer] = useState<string>(
    historyAnswers[currentKey] || ''
  )
  const [isTypingCustom, setIsTypingCustom] = useState(false)
  const [customText, setCustomText] = useState('')

  const recognitionControlsRef = useRef<SpeechRecognitionControls | null>(null)
  const fallbackTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const processingTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const isComponentMountedRef = useRef<boolean>(true)

  const clearVoiceTimers = useCallback(() => {
    if (fallbackTimerRef.current) {
      clearTimeout(fallbackTimerRef.current)
      fallbackTimerRef.current = null
    }
    if (processingTimerRef.current) {
      clearTimeout(processingTimerRef.current)
      processingTimerRef.current = null
    }
  }, [])

  const abortActiveRecognition = useCallback(() => {
    if (recognitionControlsRef.current) {
      try {
        recognitionControlsRef.current.abort()
      } catch {
        // ignore
      }
      recognitionControlsRef.current = null
    }
  }, [])

  // Audio instruction for current question
  const {
    status: instructionStatus,
    currentRepetition,
    totalRepetitions,
    isPlaying: isInstructionPlaying,
    replay: replayInstruction,
    stopPlayback,
  } = useInstructionPlayer({
    instruction: `${questionData.title} ${t.page6_history.dualInputHint}`,
    repeatCount: 1,
    autoPlay: true,
    langCode: selectedLanguage.code,
    isMuted,
  })

  // Sync state when advancing questions
  useEffect(() => {
    abortActiveRecognition()
    clearVoiceTimers()
    stopSpeaking()
    setIsListening(false)
    setIsProcessing(false)
    setLiveTranscript('')
    setIsTypingCustom(false)
    setCustomText('')
    setCurrentAnswer(historyAnswers[currentKey] || '')
  }, [questionIndex, currentKey, historyAnswers, abortActiveRecognition, clearVoiceTimers])

  useEffect(() => {
    isComponentMountedRef.current = true
    return () => {
      isComponentMountedRef.current = false
      clearVoiceTimers()
      abortActiveRecognition()
      stopSpeaking()
    }
  }, [clearVoiceTimers, abortActiveRecognition])

  // Real Speech Recognition with graceful fallback
  const handleStartVoice = () => {
    stopPlayback()
    stopSpeaking()
    abortActiveRecognition()
    clearVoiceTimers()
    setIsTypingCustom(false)
    setIsListening(true)
    setIsProcessing(false)
    setLiveTranscript('')

    let hasReceivedFinal = false

    // Safety fallback timer (3.6s)
    fallbackTimerRef.current = setTimeout(() => {
      if (!isComponentMountedRef.current || hasReceivedFinal) return
      abortActiveRecognition()
      setIsListening(false)
      setIsProcessing(true)

      processingTimerRef.current = setTimeout(() => {
        if (!isComponentMountedRef.current) return
        setIsProcessing(false)
        const mockVoiceResult = questionData.mockAnswer
        setCurrentAnswer(mockVoiceResult)
        setAnswerForQuestion(currentKey, questionData.title, mockVoiceResult)
      }, 900)
    }, 3600)

    // Start browser SpeechRecognition
    const controls = startSpeechRecognition(selectedLanguage.code, {
      onResult: (transcriptText, isFinal) => {
        if (!isComponentMountedRef.current) return
        setLiveTranscript(transcriptText)

        if (isFinal && transcriptText.trim()) {
          hasReceivedFinal = true
          clearVoiceTimers()
          abortActiveRecognition()
          setIsListening(false)
          setIsProcessing(true)

          processingTimerRef.current = setTimeout(() => {
            if (!isComponentMountedRef.current) return
            setIsProcessing(false)
            setCurrentAnswer(transcriptText.trim())
            setAnswerForQuestion(currentKey, questionData.title, transcriptText.trim())
          }, 700)
        }
      },
      onEnd: (finalTranscript) => {
        if (!isComponentMountedRef.current || hasReceivedFinal) return
        if (finalTranscript.trim()) {
          hasReceivedFinal = true
          clearVoiceTimers()
          setIsListening(false)
          setIsProcessing(true)

          processingTimerRef.current = setTimeout(() => {
            if (!isComponentMountedRef.current) return
            setIsProcessing(false)
            setCurrentAnswer(finalTranscript.trim())
            setAnswerForQuestion(currentKey, questionData.title, finalTranscript.trim())
          }, 700)
        }
      },
      onError: (err) => {
        console.warn('[SpeechRecognition on Page 6 Notice]:', err?.error || err)
      },
    })

    recognitionControlsRef.current = controls
  }

  // Touch Option Selection
  const handleSelectOption = (optionLabel: string) => {
    stopPlayback()
    stopSpeaking()
    abortActiveRecognition()
    clearVoiceTimers()
    setIsListening(false)
    setIsProcessing(false)
    setIsTypingCustom(false)
    setCurrentAnswer(optionLabel)
    setAnswerForQuestion(currentKey, questionData.title, optionLabel)
  }

  // Skip / Not Sure
  const handleSkip = () => {
    stopPlayback()
    stopSpeaking()
    abortActiveRecognition()
    clearVoiceTimers()
    setIsListening(false)
    setIsProcessing(false)
    const skipLabel = t.common.skip
    setCurrentAnswer(skipLabel)
    setAnswerForQuestion(currentKey, questionData.title, skipLabel)
    advanceNext(skipLabel)
  }

  // Submit custom typed answer
  const handleSubmitCustom = (e: React.FormEvent) => {
    e.preventDefault()
    if (customText.trim()) {
      stopPlayback()
      stopSpeaking()
      abortActiveRecognition()
      clearVoiceTimers()
      setCurrentAnswer(customText.trim())
      setAnswerForQuestion(currentKey, questionData.title, customText.trim())
      setIsTypingCustom(false)
    }
  }

  const advanceNext = (overrideAnswer?: string) => {
    stopPlayback()
    stopSpeaking()
    abortActiveRecognition()
    clearVoiceTimers()

    const finalAnswer = overrideAnswer || currentAnswer
    if (finalAnswer) {
      setAnswerForQuestion(currentKey, questionData.title, finalAnswer)
    }

    if (questionIndex + 1 < QUESTION_KEYS.length) {
      setQuestionIndex((prev) => prev + 1)
    } else {
      goTo('documents')
    }
  }

  const handlePreviousQuestion = () => {
    stopPlayback()
    stopSpeaking()
    abortActiveRecognition()
    clearVoiceTimers()

    if (questionIndex > 0) {
      setQuestionIndex((prev) => prev - 1)
    } else {
      goBack()
    }
  }

  const optionsList = Object.values(questionData.options)

  return (
    <div className="flex flex-col items-center justify-between h-full max-w-4xl w-full mx-auto px-6 py-1 select-none">
      {/* Question Counter & Header - Desktop First */}
      <div className="text-center my-2 max-w-2xl">
        <span className="text-xs uppercase font-bold tracking-widest text-[#2F7D73] bg-[#DCEDEA] px-3.5 py-1 rounded-full">
          Question {questionIndex + 1} of {QUESTION_KEYS.length}
        </span>
        <h2 className="text-3xl sm:text-4xl font-bold text-[#243331] mt-2 mb-1 tracking-tight">
          {questionData.title}
        </h2>
        <p className="text-base sm:text-lg text-[#647471] font-medium">
          {questionData.subtitle}
        </p>
      </div>

      {/* Main Card (Desktop-First Wide Viewport) — scrolls internally so bottom bar stays visible */}
      <div className="flex-1 min-h-0 w-full overflow-y-auto my-1 pr-1">
        <div className="w-full bg-white border border-[#D9E2DF] rounded-3xl p-6 sm:p-8 shadow-sm space-y-6">
          {/* Top: Voice & Manual Speak Trigger */}
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 bg-[#F9FBFA] rounded-2xl border border-[#D9E2DF]">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-2xl bg-[#DCEDEA] text-[#2F7D73] flex items-center justify-center flex-shrink-0">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                </svg>
              </div>
              <div>
                <h4 className="text-base font-bold text-[#243331]">
                  {t.page6_history.startVoiceBtn}
                </h4>
                <p className="text-xs text-[#647471]">
                  {isListening
                    ? liveTranscript
                      ? `"${liveTranscript}"`
                      : t.page6_history.listening
                    : isProcessing
                      ? t.page6_history.processing
                      : 'Tap to speak your answer'}
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {isListening ? (
                <div className="flex items-center gap-2 px-4 py-2 bg-[#E8F4F1] border border-[#2F7D73] text-[#2F7D73] rounded-xl text-sm font-bold animate-pulse">
                  <span className="w-2.5 h-2.5 rounded-full bg-[#2F7D73]" />
                  <span>{t.page6_history.listening}</span>
                </div>
              ) : isProcessing ? (
                <div className="flex items-center gap-2 px-4 py-2 bg-[#EFF6FF] border border-[#2563EB] text-[#2563EB] rounded-xl text-sm font-bold animate-pulse">
                  <span>{t.page6_history.processing}</span>
                </div>
              ) : (
                <button
                  type="button"
                  onClick={handleStartVoice}
                  className="px-5 py-2.5 bg-[#2F7D73] hover:bg-[#276B63] text-white font-bold rounded-xl text-sm shadow-xs transition-colors cursor-pointer flex items-center gap-2"
                >
                  <span>🎤 {t.page6_history.startVoiceBtn}</span>
                </button>
              )}
            </div>
          </div>

          {/* Display Captured Answer if available */}
          {currentAnswer && (
            <div className="p-4 bg-[#EBF4EE] border-2 border-[#4F8A6D] rounded-2xl flex items-center justify-between gap-4 animate-fade-in">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-[#4F8A6D] block mb-0.5">
                  Selected Answer:
                </span>
                <p className="text-lg font-bold text-[#243331]">
                  "{currentAnswer}"
                </p>
              </div>
              <button
                type="button"
                onClick={() => setCurrentAnswer('')}
                className="text-xs font-semibold text-[#647471] hover:text-[#B85C5C] px-3 py-1.5 rounded-lg border border-[#D9E2DF] bg-white cursor-pointer"
              >
                Clear
              </button>
            </div>
          )}

          {/* Center: Touch Options Grid (2x2) */}
          <div>
            <p className="text-xs font-bold uppercase tracking-wider text-[#647471] mb-3">
              {t.page6_history.orTapBelow}
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
              {optionsList.map((label, idx) => {
                const isSelected = currentAnswer === label

                return (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleSelectOption(label)}
                    className={`py-4 px-6 rounded-2xl border-2 text-base sm:text-lg font-bold transition-all cursor-pointer text-left flex items-center justify-between ${isSelected
                        ? 'bg-[#EBF4EE] border-[#4F8A6D] text-[#243331] shadow-xs'
                        : 'bg-[#FFFFFF] border-[#D9E2DF] hover:border-[#2F7D73] hover:bg-[#F9FBFA] text-[#243331]'
                      }`}
                  >
                    <span>{label}</span>
                    <div
                      className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${isSelected
                          ? 'bg-[#4F8A6D] border-[#4F8A6D] text-white'
                          : 'border-[#D9E2DF] bg-white'
                        }`}
                    >
                      {isSelected && (
                        <svg className="w-3.5 h-3.5 stroke-current stroke-3" fill="none" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </div>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Custom Typing Fallback toggle */}
          <div className="pt-1">
            {isTypingCustom ? (
              <form onSubmit={handleSubmitCustom} className="flex gap-2">
                <input
                  type="text"
                  value={customText}
                  onChange={(e) => setCustomText(e.target.value)}
                  placeholder={t.page6_history.typePlaceholder}
                  className="flex-1 px-4 py-3 border border-[#D9E2DF] rounded-xl text-base text-[#243331] outline-none focus:border-[#2F7D73]"
                  autoFocus
                />
                <button
                  type="submit"
                  className="px-5 py-3 bg-[#4F8A6D] text-white font-bold rounded-xl text-sm cursor-pointer"
                >
                  {t.common.save}
                </button>
                <button
                  type="button"
                  onClick={() => setIsTypingCustom(false)}
                  className="px-4 py-3 border border-[#D9E2DF] text-[#647471] rounded-xl text-sm cursor-pointer"
                >
                  {t.common.cancel}
                </button>
              </form>
            ) : (
              <button
                type="button"
                onClick={() => {
                  abortActiveRecognition()
                  clearVoiceTimers()
                  setIsTypingCustom(true)
                }}
                className="text-xs font-semibold text-[#647471] hover:text-[#2F7D73] flex items-center gap-1.5 cursor-pointer"
              >
                <span>⌨ {t.page6_history.typePlaceholder}</span>
              </button>
            )}
          </div>

          {/* Prominent Skip / Not Sure Button */}
          <div className="pt-2 border-t border-[#EBF0EE] flex justify-center">
            <button
              type="button"
              onClick={handleSkip}
              className="w-full sm:w-auto px-8 py-3.5 rounded-2xl border-2 border-[#D9E2DF] bg-[#F6F8F7] hover:bg-[#E2E8F0] active:bg-[#CBD5E1] text-[#647471] hover:text-[#243331] font-bold text-base transition-colors cursor-pointer flex items-center justify-center gap-2 shadow-xs min-h-[48px]"
            >
              <svg className="w-5 h-5 text-[#647471]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
              </svg>
              <span>{t.page6_history.skipNotSure}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Bottom Bar: Back + Hear Again + Next */}
      <div className="w-full flex items-center justify-between mt-auto pt-3 pb-0.5 border-t border-[#D9E2DF]">
        <button
          type="button"
          onClick={handlePreviousQuestion}
          className="px-6 py-3.5 rounded-xl border border-[#D9E2DF] bg-white hover:bg-gray-50 text-base font-semibold text-[#243331] flex items-center gap-2 transition-colors cursor-pointer shadow-xs min-h-[48px]"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M15 19l-7-7 7-7" />
          </svg>
          <span>{t.common.back}</span>
        </button>

        <HearAgainButton
          onHearAgain={() => {
            abortActiveRecognition()
            clearVoiceTimers()
            setIsListening(false)
            setIsProcessing(false)
            replayInstruction()
          }}
          status={instructionStatus}
          currentRepetition={currentRepetition}
          totalRepetitions={totalRepetitions}
          isPlaying={isInstructionPlaying}
        />

        <button
          type="button"
          onClick={() => advanceNext()}
          disabled={!currentAnswer}
          className="px-8 py-3.5 bg-[#4F8A6D] hover:bg-[#3E6E56] disabled:opacity-40 active:bg-[#335B47] text-white font-bold text-base rounded-xl shadow-md flex items-center gap-2 transition-all cursor-pointer min-h-[48px]"
        >
          <span>{t.common.next}</span>
          <svg className="w-5 h-5 stroke-current stroke-2" fill="none" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
          </svg>
        </button>
      </div>
    </div>
  )
}
