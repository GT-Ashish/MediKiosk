import React, { useState, useRef, useEffect, useCallback } from 'react'
import { useKiosk } from '../../context/KioskContext'
import { useInstructionPlayer } from '../../hooks/useInstructionPlayer'
import { HearAgainButton } from '../../components/patient/HearAgainButton'
import {
  startSpeechRecognition,
  stopSpeaking,
  type SpeechRecognitionControls,
} from '../../utils/speech'

type Page5State =
  | 'INSTRUCTION_PLAYING'
  | 'IDLE'
  | 'LISTENING'
  | 'PROCESSING'
  | 'SHOWING_TRANSCRIPT'
  | 'TYPING'
  | 'SUBMITTED'

export const ComplaintPage: React.FC = () => {
  const {
    t,
    selectedLanguage,
    isMuted,
    chiefComplaint,
    setChiefComplaint,
    goTo,
    goBack,
  } = useKiosk()

  const [state, setState] = useState<Page5State>('INSTRUCTION_PLAYING')
  const [typedText, setTypedText] = useState<string>(chiefComplaint || '')
  const [liveTranscript, setLiveTranscript] = useState<string>('')
  const [inputSource, setInputSource] = useState<'voice_real' | 'voice_mock' | 'typed' | null>(null)

  const recognitionControlsRef = useRef<SpeechRecognitionControls | null>(null)
  const fallbackTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const processingTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const isComponentMountedRef = useRef<boolean>(true)

  const clearAllVoiceTimers = useCallback(() => {
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

  // Instruction plays once on entry
  const {
    status: instructionStatus,
    currentRepetition,
    totalRepetitions,
    isPlaying: isInstructionPlaying,
    replay: replayInstruction,
    stopPlayback,
  } = useInstructionPlayer({
    instruction: t.page5_complaint.instruction,
    repeatCount: 1,
    autoPlay: true,
    langCode: selectedLanguage.code,
    isMuted,
    onComplete: () => {
      // Once instruction finishes, move to IDLE choice state without mic running
      setState((prev) => (prev === 'INSTRUCTION_PLAYING' ? 'IDLE' : prev))
    },
  })

  // Start Speech Recognition with graceful clinical fallback
  const handleStartVoice = useCallback(() => {
    // 1. Immediately cancel active TTS & audio
    stopPlayback()
    stopSpeaking()

    // 2. Abort any previous recognition & timers
    abortActiveRecognition()
    clearAllVoiceTimers()

    setLiveTranscript('')
    setState('LISTENING')

    let hasReceivedFinal = false

    // Safety / Fallback Timer: if no speech after 3.8 seconds, fallback gracefully to mock
    fallbackTimerRef.current = setTimeout(() => {
      if (!isComponentMountedRef.current || hasReceivedFinal) return
      abortActiveRecognition()
      setInputSource('voice_mock')
      setState('PROCESSING')

      processingTimerRef.current = setTimeout(() => {
        if (!isComponentMountedRef.current) return
        const transcript = t.page5_complaint.mockTranscript
        setChiefComplaint(transcript)
        setState('SHOWING_TRANSCRIPT')
      }, 1000)
    }, 3800)

    // 3. Start real browser SpeechRecognition
    const controls = startSpeechRecognition(selectedLanguage.code, {
      onResult: (transcriptText, isFinal) => {
        if (!isComponentMountedRef.current) return
        setLiveTranscript(transcriptText)

        if (isFinal && transcriptText.trim()) {
          hasReceivedFinal = true
          clearAllVoiceTimers()
          abortActiveRecognition()

          setInputSource('voice_real')
          setChiefComplaint(transcriptText.trim())
          setState('PROCESSING')

          processingTimerRef.current = setTimeout(() => {
            if (!isComponentMountedRef.current) return
            setState('SHOWING_TRANSCRIPT')
          }, 800)
        }
      },
      onEnd: (finalTranscript) => {
        if (!isComponentMountedRef.current || hasReceivedFinal) return
        if (finalTranscript.trim()) {
          hasReceivedFinal = true
          clearAllVoiceTimers()
          setInputSource('voice_real')
          setChiefComplaint(finalTranscript.trim())
          setState('PROCESSING')

          processingTimerRef.current = setTimeout(() => {
            if (!isComponentMountedRef.current) return
            setState('SHOWING_TRANSCRIPT')
          }, 800)
        }
      },
      onError: (err) => {
        // If recognition failed/denied, fallback timer or immediate fallback completes cleanly
        console.warn('[SpeechRecognition on Page 5 Notice]:', err?.error || err)
      },
    })

    recognitionControlsRef.current = controls
  }, [
    abortActiveRecognition,
    clearAllVoiceTimers,
    selectedLanguage.code,
    setChiefComplaint,
    stopPlayback,
    t.page5_complaint.mockTranscript,
  ])

  // Start Typing (Interrupts any voice or instruction)
  const handleStartTyping = () => {
    stopPlayback()
    stopSpeaking()
    abortActiveRecognition()
    clearAllVoiceTimers()
    setInputSource('typed')
    setState('TYPING')
  }

  // Submit Typed Response
  const handleSubmitTyping = (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    if (typedText.trim()) {
      setChiefComplaint(typedText.trim())
      setInputSource('typed')
      setState('SUBMITTED')
    }
  }

  // Hear Again Replay Handler (Stops recognition, plays TTS)
  const handleHearAgain = () => {
    abortActiveRecognition()
    clearAllVoiceTimers()
    setState('INSTRUCTION_PLAYING')
    replayInstruction()
  }

  const handleNext = () => {
    abortActiveRecognition()
    clearAllVoiceTimers()
    stopPlayback()
    stopSpeaking()
    goTo('history_taking')
  }

  const handleBack = () => {
    abortActiveRecognition()
    clearAllVoiceTimers()
    stopPlayback()
    stopSpeaking()
    goBack()
  }

  // Clean up timers, speech, and recognition on unmount
  useEffect(() => {
    isComponentMountedRef.current = true
    return () => {
      isComponentMountedRef.current = false
      clearAllVoiceTimers()
      abortActiveRecognition()
      stopSpeaking()
    }
  }, [clearAllVoiceTimers, abortActiveRecognition])

  const hasValidResponse = Boolean(chiefComplaint.trim())

  return (
    <div className="flex flex-col items-center justify-between min-h-[calc(100vh-140px)] max-w-4xl w-full mx-auto px-6 py-8 select-none">
      {/* Page Heading - Desktop First */}
      <div className="text-center my-3 max-w-2xl">
        <h2 className="text-3xl sm:text-4xl font-bold text-[#243331] mb-2 tracking-tight">
          {t.page5_complaint.title}
        </h2>
        <p className="text-base sm:text-lg text-[#647471] font-medium">
          {t.page5_complaint.subtitle}
        </p>
      </div>

      {/* Main Interaction Area (Desktop-First Wide Card) */}
      <div className="w-full bg-white border border-[#D9E2DF] rounded-3xl p-8 sm:p-10 shadow-sm my-4 flex flex-col items-center justify-center min-h-[360px]">
        {/* State 1: INSTRUCTION_PLAYING */}
        {state === 'INSTRUCTION_PLAYING' && (
          <div className="flex flex-col items-center text-center space-y-4 animate-fade-in">
            <div className="w-20 h-20 rounded-full bg-[#EFF6FF] text-[#2563EB] flex items-center justify-center animate-pulse">
              <svg className="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
              </svg>
            </div>
            <p className="text-xl font-semibold text-[#243331] max-w-lg">
              {t.page5_complaint.instruction}
            </p>
            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={handleStartVoice}
                className="px-5 py-2.5 bg-[#2F7D73] hover:bg-[#276B63] text-white font-bold rounded-xl text-sm transition-colors cursor-pointer flex items-center gap-2"
              >
                <span>🎤 {t.page5_complaint.startVoiceBtn}</span>
              </button>
              <button
                type="button"
                onClick={handleStartTyping}
                className="px-5 py-2.5 border border-[#D9E2DF] hover:bg-gray-50 text-[#243331] font-semibold rounded-xl text-sm transition-colors cursor-pointer"
              >
                {t.page5_complaint.switchToTypeBtn}
              </button>
            </div>
          </div>
        )}

        {/* State 2: IDLE (Waiting for User Choice) */}
        {state === 'IDLE' && (
          <div className="flex flex-col items-center text-center space-y-6 animate-fade-in w-full max-w-lg">
            <p className="text-lg font-bold text-[#243331]">
              How would you like to answer?
            </p>
            <div className="grid grid-cols-2 gap-4 w-full">
              <button
                type="button"
                onClick={handleStartVoice}
                className="p-6 rounded-2xl bg-[#E8F4F1] border-2 border-[#2F7D73] hover:bg-[#DCEDEA] text-[#2F7D73] flex flex-col items-center justify-center gap-3 transition-all cursor-pointer group shadow-xs"
              >
                <div className="w-16 h-16 rounded-full bg-[#2F7D73] text-white flex items-center justify-center shadow-md group-hover:scale-105 transition-transform">
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                  </svg>
                </div>
                <span className="text-lg font-bold">{t.page5_complaint.startVoiceBtn}</span>
              </button>

              <button
                type="button"
                onClick={handleStartTyping}
                className="p-6 rounded-2xl bg-[#F6F8F7] border-2 border-[#D9E2DF] hover:border-[#2F7D73] hover:bg-white text-[#243331] flex flex-col items-center justify-center gap-3 transition-all cursor-pointer group shadow-xs"
              >
                <div className="w-16 h-16 rounded-full bg-[#647471] text-white flex items-center justify-center shadow-md group-hover:scale-105 transition-transform">
                  <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </div>
                <span className="text-lg font-bold">{t.page5_complaint.switchToTypeBtn}</span>
              </button>
            </div>
          </div>
        )}

        {/* State 3: LISTENING (Microphone Owns Interaction) */}
        {state === 'LISTENING' && (
          <div className="flex flex-col items-center text-center space-y-4 animate-fade-in w-full max-w-lg">
            <div className="relative flex items-center justify-center">
              <div className="absolute w-28 h-28 rounded-full bg-[#2F7D73] opacity-20 animate-ping pointer-events-none" />
              <div className="w-24 h-24 rounded-full bg-[#2F7D73] text-white flex items-center justify-center shadow-lg">
                <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                </svg>
              </div>
            </div>

            <h3 className="text-2xl font-bold text-[#243331]">
              {t.page5_complaint.listening}
            </h3>

            {/* Pulsing Waveform Bars */}
            <div className="flex items-center gap-1.5 h-10 my-1">
              {[16, 28, 38, 22, 34, 18, 30, 14].map((h, i) => (
                <div
                  key={i}
                  className="w-1.5 bg-[#2F7D73] rounded-full animate-wave-bar"
                  style={{ height: `${h}px`, animationDelay: `${i * 0.1}s` }}
                />
              ))}
            </div>

            {/* Live Interim Transcript */}
            {liveTranscript ? (
              <div className="w-full bg-[#F0FDF4] border border-[#86EFAC] rounded-xl px-4 py-2.5 text-sm text-[#166534] font-medium animate-fade-in">
                <span className="font-bold text-xs uppercase block text-[#15803D] mb-0.5">Speaking:</span>
                "{liveTranscript}"
              </div>
            ) : (
              <p className="text-xs text-[#647471]">
                Speak clearly into your microphone...
              </p>
            )}

            <button
              type="button"
              onClick={handleStartTyping}
              className="text-xs text-[#647471] hover:text-[#2F7D73] underline cursor-pointer mt-1"
            >
              Switch to typing instead
            </button>
          </div>
        )}

        {/* State 4: PROCESSING */}
        {state === 'PROCESSING' && (
          <div className="flex flex-col items-center text-center space-y-4 animate-fade-in">
            <div className="w-20 h-20 rounded-full border-4 border-[#2F7D73] border-t-transparent animate-spin" />
            <h3 className="text-xl font-bold text-[#243331]">
              {t.page5_complaint.processing}
            </h3>
          </div>
        )}

        {/* State 5: SHOWING_TRANSCRIPT (Voice Success) */}
        {state === 'SHOWING_TRANSCRIPT' && (
          <div className="flex flex-col items-center text-center w-full max-w-xl space-y-5 animate-fade-in">
            <div className="w-12 h-12 rounded-full bg-[#EBF4EE] text-[#4F8A6D] flex items-center justify-center">
              <svg className="w-7 h-7 stroke-current stroke-2" fill="none" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            </div>

            <div className="w-full bg-[#F6F8F7] border-2 border-[#2F7D73] rounded-2xl p-5 text-left shadow-xs">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs font-bold uppercase tracking-wider text-[#2F7D73]">
                  {t.page5_complaint.youSaid}
                </span>
                {inputSource === 'voice_real' && (
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-[#DCEDEA] text-[#2F7D73]">
                    ✓ Microphone Captured
                  </span>
                )}
              </div>
              <p className="text-xl font-semibold text-[#243331] italic">
                "{chiefComplaint}"
              </p>
            </div>

            {/* Retry or Confirm Actions */}
            <div className="flex items-center gap-3 w-full">
              <button
                type="button"
                onClick={handleStartVoice}
                className="flex-1 py-3.5 px-4 rounded-xl border border-[#D9E2DF] bg-white hover:bg-gray-50 text-[#243331] font-semibold text-base transition-colors cursor-pointer flex items-center justify-center gap-2"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                <span>{t.common.retry}</span>
              </button>

              <button
                type="button"
                onClick={handleStartTyping}
                className="flex-1 py-3.5 px-4 rounded-xl border border-[#D9E2DF] bg-white hover:bg-gray-50 text-[#243331] font-semibold text-base transition-colors cursor-pointer"
              >
                <span>{t.common.edit} (Type)</span>
              </button>

              <button
                type="button"
                onClick={handleNext}
                className="flex-1 py-3.5 px-6 rounded-xl bg-[#4F8A6D] hover:bg-[#3E6E56] text-white font-bold text-base shadow-md transition-all cursor-pointer flex items-center justify-center gap-2"
              >
                <span>{t.common.next}</span>
                <svg className="w-4 h-4 stroke-current stroke-2" fill="none" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </button>
            </div>
          </div>
        )}

        {/* State 6: TYPING */}
        {state === 'TYPING' && (
          <form onSubmit={handleSubmitTyping} className="w-full max-w-xl space-y-4 animate-fade-in">
            <label className="text-base font-bold text-[#243331] block">
              {t.page5_complaint.title}
            </label>
            <textarea
              value={typedText}
              onChange={(e) => setTypedText(e.target.value)}
              placeholder={t.page5_complaint.typePlaceholder}
              className="w-full h-32 p-4 bg-white border-2 border-[#2F7D73] rounded-2xl text-lg text-[#243331] outline-none shadow-xs resize-none"
              autoFocus
            />

            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => setState(chiefComplaint ? 'SUBMITTED' : 'IDLE')}
                className="px-5 py-3 border border-[#D9E2DF] bg-white hover:bg-gray-50 text-[#647471] font-semibold rounded-xl text-base cursor-pointer"
              >
                {t.common.cancel}
              </button>

              <button
                type="button"
                onClick={handleStartVoice}
                className="px-5 py-3 border border-[#2F7D73] text-[#2F7D73] hover:bg-[#DCEDEA] font-semibold rounded-xl text-base flex items-center gap-2 cursor-pointer"
              >
                <span>🎤 {t.page5_complaint.startVoiceBtn}</span>
              </button>

              <button
                type="submit"
                disabled={!typedText.trim()}
                className="flex-1 py-3 bg-[#4F8A6D] hover:bg-[#3E6E56] disabled:opacity-50 text-white font-bold rounded-xl text-base shadow-md transition-all cursor-pointer"
              >
                {t.common.submit}
              </button>
            </div>
          </form>
        )}

        {/* State 7: SUBMITTED (Typed Response Verified) */}
        {state === 'SUBMITTED' && (
          <div className="flex flex-col items-center text-center w-full max-w-xl space-y-5 animate-fade-in">
            <div className="w-12 h-12 rounded-full bg-[#EBF4EE] text-[#4F8A6D] flex items-center justify-center">
              <svg className="w-7 h-7 stroke-current stroke-2" fill="none" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            </div>

            <div className="w-full bg-[#F6F8F7] border-2 border-[#4F8A6D] rounded-2xl p-5 text-left shadow-xs">
              <span className="text-xs font-bold uppercase tracking-wider text-[#4F8A6D] block mb-1">
                {t.page5_complaint.youEntered}
              </span>
              <p className="text-xl font-semibold text-[#243331]">
                "{chiefComplaint}"
              </p>
            </div>

            <div className="flex items-center gap-3 w-full">
              <button
                type="button"
                onClick={handleStartTyping}
                className="flex-1 py-3.5 px-4 rounded-xl border border-[#D9E2DF] bg-white hover:bg-gray-50 text-[#243331] font-semibold text-base transition-colors cursor-pointer"
              >
                {t.common.edit}
              </button>

              <button
                type="button"
                onClick={handleStartVoice}
                className="flex-1 py-3.5 px-4 rounded-xl border border-[#D9E2DF] bg-white hover:bg-gray-50 text-[#2F7D73] font-semibold text-base transition-colors cursor-pointer"
              >
                🎤 {t.common.retry}
              </button>

              <button
                type="button"
                onClick={handleNext}
                className="flex-1 py-3.5 px-6 rounded-xl bg-[#4F8A6D] hover:bg-[#3E6E56] text-white font-bold text-base shadow-md transition-all cursor-pointer flex items-center justify-center gap-2"
              >
                <span>{t.common.next}</span>
                <svg className="w-4 h-4 stroke-current stroke-2" fill="none" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Bottom Bar: Back + Hear Again + Next (Desktop Layout) */}
      <div className="w-full flex items-center justify-between mt-auto pt-4 border-t border-[#D9E2DF]">
        <button
          type="button"
          onClick={handleBack}
          className="px-6 py-3.5 rounded-xl border border-[#D9E2DF] bg-white hover:bg-gray-50 text-base font-semibold text-[#243331] flex items-center gap-2 transition-colors cursor-pointer shadow-xs min-h-[48px]"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M15 19l-7-7 7-7" />
          </svg>
          <span>{t.common.back}</span>
        </button>

        <HearAgainButton
          onHearAgain={handleHearAgain}
          status={instructionStatus}
          currentRepetition={currentRepetition}
          totalRepetitions={totalRepetitions}
          isPlaying={isInstructionPlaying}
        />

        {hasValidResponse ? (
          <button
            type="button"
            onClick={handleNext}
            className="px-7 py-3.5 bg-[#4F8A6D] hover:bg-[#3E6E56] active:bg-[#335B47] text-white font-bold text-base rounded-xl shadow-md flex items-center gap-2 transition-all cursor-pointer min-h-[48px]"
          >
            <span>{t.common.next}</span>
            <svg className="w-5 h-5 stroke-current stroke-2" fill="none" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </button>
        ) : (
          <div className="w-24" />
        )}
      </div>
    </div>
  )
}
