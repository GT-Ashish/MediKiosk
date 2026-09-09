import { useState, useEffect, useRef, useCallback } from 'react'
import type { InstructionStatus } from '../types'

const REPLAY_REMINDER = 'To hear this instruction again, press the blue Hear Again button at the bottom.'

interface UseInstructionPlayerProps {
  instruction: string
  repeatCount?: number // Usually 2 or 3
  autoPlay?: boolean
  languageCode?: string
}

interface UseInstructionPlayerReturn {
  status: InstructionStatus
  currentRepetition: number
  totalRepetitions: number
  isFinalRepetition: boolean
  isPlaying: boolean
  currentSpokenText: string
  replay: () => void
}

export function useInstructionPlayer({
  instruction,
  repeatCount = 2,
  autoPlay = true,
  languageCode = 'en-US',
}: UseInstructionPlayerProps): UseInstructionPlayerReturn {
  const [status, setStatus] = useState<InstructionStatus>('IDLE')
  const [currentRepetition, setCurrentRepetition] = useState<number>(1)
  const isPlayingRef = useRef<boolean>(false)
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const activeUtteranceRef = useRef<SpeechSynthesisUtterance | null>(null)
  const playRepetitionRef = useRef<(repIndex: number) => void>(() => {})

  const isFinalRepetition = currentRepetition === repeatCount

  // The spoken text: normal instruction on initial repeats, with reminder on the final repeat
  const currentSpokenText = isFinalRepetition
    ? `${instruction} ${REPLAY_REMINDER}`
    : instruction

  const stopAllPlayback = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current)
      timerRef.current = null
    }
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      try {
        window.speechSynthesis.cancel()
      } catch {
        // Silently handle if speech synthesis fails
      }
    }
    isPlayingRef.current = false
  }, [])

  const fallbackTimerSimulation = useCallback(
    (repIndex: number, textLength: number) => {
      // Approximate speaking duration: ~55ms per character, minimum 2.5s
      const simulatedDuration = Math.max(2500, textLength * 55)

      timerRef.current = setTimeout(() => {
        if (!isPlayingRef.current) return
        if (repIndex < repeatCount) {
          timerRef.current = setTimeout(() => {
            playRepetitionRef.current(repIndex + 1)
          }, 800)
        } else {
          isPlayingRef.current = false
          setStatus('COMPLETED')
        }
      }, simulatedDuration)
    },
    [repeatCount],
  )

  const playRepetition = useCallback(
    (repIndex: number) => {
      stopAllPlayback()

      const isFinal = repIndex === repeatCount
      setCurrentRepetition(repIndex)
      setStatus(isFinal ? 'FINAL_REPETITION' : 'PLAYING')
      isPlayingRef.current = true

      const textToSpeak = isFinal ? `${instruction} ${REPLAY_REMINDER}` : instruction

      // Try browser Web Speech API
      const hasSpeechSynth = typeof window !== 'undefined' && 'speechSynthesis' in window

      if (hasSpeechSynth) {
        try {
          const utterance = new SpeechSynthesisUtterance(textToSpeak)
          utterance.lang = languageCode
          utterance.rate = 0.92 // Calm clinical pace
          utterance.pitch = 1.0

          activeUtteranceRef.current = utterance

          utterance.onend = () => {
            if (!isPlayingRef.current) return
            if (repIndex < repeatCount) {
              timerRef.current = setTimeout(() => {
                playRepetitionRef.current(repIndex + 1)
              }, 900)
            } else {
              isPlayingRef.current = false
              setStatus('COMPLETED')
            }
          }

          utterance.onerror = () => {
            fallbackTimerSimulation(repIndex, textToSpeak.length)
          }

          window.speechSynthesis.speak(utterance)
          return
        } catch {
          // Continue to fallback simulation
        }
      }

      fallbackTimerSimulation(repIndex, textToSpeak.length)
    },
    [instruction, repeatCount, languageCode, stopAllPlayback, fallbackTimerSimulation],
  )

  // Keep ref up to date
  useEffect(() => {
    playRepetitionRef.current = playRepetition
  }, [playRepetition])

  // Restart the complete instruction loop from repetition 1
  const replay = useCallback(() => {
    stopAllPlayback()
    setStatus('REPLAYING')
    setCurrentRepetition(1)
    setTimeout(() => {
      playRepetition(1)
    }, 100)
  }, [playRepetition, stopAllPlayback])

  // Automatically start playback on mount or when instruction changes
  useEffect(() => {
    if (autoPlay && instruction) {
      const startTimer = setTimeout(() => {
        playRepetition(1)
      }, 400)
      return () => {
        clearTimeout(startTimer)
        stopAllPlayback()
      }
    }
    return () => {
      stopAllPlayback()
    }
  }, [instruction, autoPlay, playRepetition, stopAllPlayback])

  return {
    status,
    currentRepetition,
    totalRepetitions: repeatCount,
    isFinalRepetition,
    isPlaying: status === 'PLAYING' || status === 'FINAL_REPETITION' || status === 'REPLAYING',
    currentSpokenText,
    replay,
  }
}
