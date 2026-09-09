import { useState, useEffect, useRef, useCallback } from 'react'
import type { InstructionStatus } from '../types'
import { getReplayReminder } from '../i18n'
import { speakText, stopSpeaking } from '../utils/speech'

interface UseInstructionPlayerProps {
  instruction: string
  repeatCount?: number // Usually 1, 2 or 3
  autoPlay?: boolean
  langCode?: string
  isMuted?: boolean
  onComplete?: () => void
}

interface UseInstructionPlayerReturn {
  status: InstructionStatus
  currentRepetition: number
  totalRepetitions: number
  isFinalRepetition: boolean
  isPlaying: boolean
  currentSpokenText: string
  replay: () => void
  stopPlayback: () => void
}

export function useInstructionPlayer({
  instruction,
  repeatCount = 2,
  autoPlay = true,
  langCode = 'en',
  isMuted = false,
  onComplete,
}: UseInstructionPlayerProps): UseInstructionPlayerReturn {
  const [status, setStatus] = useState<InstructionStatus>('IDLE')
  const [currentRepetition, setCurrentRepetition] = useState<number>(1)
  const isPlayingRef = useRef<boolean>(false)
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const safetyTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const cancelSpeechRef = useRef<(() => void) | null>(null)
  const playRepetitionRef = useRef<(repIndex: number) => void>(() => {})
  const onCompleteRef = useRef<(() => void) | undefined>(onComplete)

  useEffect(() => {
    onCompleteRef.current = onComplete
  }, [onComplete])

  const isFinalRepetition = currentRepetition === repeatCount
  const replayReminder = getReplayReminder(langCode)

  // Spoken text: normal instruction on initial repeats, with reminder on final repeat
  const currentSpokenText = isFinalRepetition
    ? `${instruction} ${replayReminder}`
    : instruction

  const clearAllTimers = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current)
      timerRef.current = null
    }
    if (safetyTimerRef.current) {
      clearTimeout(safetyTimerRef.current)
      safetyTimerRef.current = null
    }
  }, [])

  const stopPlayback = useCallback(() => {
    clearAllTimers()
    if (cancelSpeechRef.current) {
      cancelSpeechRef.current()
      cancelSpeechRef.current = null
    } else {
      stopSpeaking()
    }
    isPlayingRef.current = false
    setStatus('COMPLETED')
  }, [clearAllTimers])

  const playRepetition = useCallback(
    (repIndex: number) => {
      clearAllTimers()
      if (cancelSpeechRef.current) {
        cancelSpeechRef.current()
        cancelSpeechRef.current = null
      } else {
        stopSpeaking()
      }

      if (isMuted) {
        isPlayingRef.current = false
        setStatus('COMPLETED')
        if (onCompleteRef.current) onCompleteRef.current()
        return
      }

      const isFinal = repIndex === repeatCount
      setCurrentRepetition(repIndex)
      setStatus(isFinal ? 'FINAL_REPETITION' : 'PLAYING')
      isPlayingRef.current = true

      const textToSpeak = isFinal ? `${instruction} ${replayReminder}` : instruction

      const handleSpeechComplete = () => {
        clearAllTimers()
        if (!isPlayingRef.current) return

        if (repIndex < repeatCount) {
          // Pause between repetitions (~600ms)
          timerRef.current = setTimeout(() => {
            playRepetitionRef.current(repIndex + 1)
          }, 600)
        } else {
          // Final repetition complete — stop cleanly
          isPlayingRef.current = false
          setStatus('COMPLETED')
          if (onCompleteRef.current) {
            onCompleteRef.current()
          }
        }
      }

      // Safety timeout: in case the browser voice engine stalls or fails to fire onend
      const safetyDuration = Math.max(4500, textToSpeak.length * 85 + 2500)
      safetyTimerRef.current = setTimeout(() => {
        handleSpeechComplete()
      }, safetyDuration)

      // Start actual browser-native speech synthesis
      cancelSpeechRef.current = speakText(textToSpeak, langCode, {
        onEnd: () => {
          handleSpeechComplete()
        },
        onError: () => {
          // If speech synthesis encountered an error, proceed safely
          handleSpeechComplete()
        },
      })
    },
    [clearAllTimers, instruction, isMuted, langCode, repeatCount, replayReminder]
  )

  useEffect(() => {
    playRepetitionRef.current = playRepetition
  }, [playRepetition])

  // Restart the instruction loop from repetition 1
  const replay = useCallback(() => {
    clearAllTimers()
    setStatus('REPLAYING')
    setCurrentRepetition(1)
    const tId = setTimeout(() => {
      playRepetition(1)
    }, 60)
    timerRef.current = tId
  }, [clearAllTimers, playRepetition])

  // Automatically start playback on mount or when instruction/language changes
  useEffect(() => {
    if (autoPlay && instruction && !isMuted) {
      const startTimer = setTimeout(() => {
        playRepetition(1)
      }, 350)
      return () => {
        clearTimeout(startTimer)
        clearAllTimers()
        if (cancelSpeechRef.current) {
          cancelSpeechRef.current()
          cancelSpeechRef.current = null
        } else {
          stopSpeaking()
        }
      }
    } else if (isMuted) {
      stopPlayback()
    }

    return () => {
      clearAllTimers()
      if (cancelSpeechRef.current) {
        cancelSpeechRef.current()
        cancelSpeechRef.current = null
      } else {
        stopSpeaking()
      }
    }
  }, [instruction, autoPlay, isMuted, langCode, playRepetition, stopPlayback, clearAllTimers])

  return {
    status,
    currentRepetition,
    totalRepetitions: repeatCount,
    isFinalRepetition,
    isPlaying: (status === 'PLAYING' || status === 'FINAL_REPETITION' || status === 'REPLAYING') && !isMuted,
    currentSpokenText,
    replay,
    stopPlayback,
  }
}
