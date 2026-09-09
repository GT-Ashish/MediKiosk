import { useState, useEffect, useRef, useCallback } from 'react'
import type { InstructionStatus } from '../types'
import { getReplayReminder } from '../i18n'

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
  const playRepetitionRef = useRef<(repIndex: number) => void>(() => {})

  const isFinalRepetition = currentRepetition === repeatCount
  const replayReminder = getReplayReminder(langCode)

  // Spoken text: normal instruction on initial repeats, with reminder on final repeat
  const currentSpokenText = isFinalRepetition
    ? `${instruction} ${replayReminder}`
    : instruction

  const stopPlayback = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current)
      timerRef.current = null
    }
    isPlayingRef.current = false
    setStatus('COMPLETED')
  }, [])

  const simulateSpeech = useCallback(
    (repIndex: number, textLength: number) => {
      // If muted, do not play audio simulation; complete immediately
      if (isMuted) {
        isPlayingRef.current = false
        setStatus('COMPLETED')
        if (onComplete) onComplete()
        return
      }

      // Calm clinical speaking duration simulation: ~40ms per char, min 2000ms
      const simulatedDuration = Math.max(2000, textLength * 40)

      timerRef.current = setTimeout(() => {
        if (!isPlayingRef.current) return

        if (repIndex < repeatCount) {
          // Pause between repetitions
          timerRef.current = setTimeout(() => {
            playRepetitionRef.current(repIndex + 1)
          }, 700)
        } else {
          // Final repetition complete — STOP cleanly
          isPlayingRef.current = false
          setStatus('COMPLETED')
          if (onComplete) {
            onComplete()
          }
        }
      }, simulatedDuration)
    },
    [repeatCount, isMuted, onComplete],
  )

  const playRepetition = useCallback(
    (repIndex: number) => {
      if (timerRef.current) {
        clearTimeout(timerRef.current)
        timerRef.current = null
      }

      if (isMuted) {
        isPlayingRef.current = false
        setStatus('COMPLETED')
        if (onComplete) onComplete()
        return
      }

      const isFinal = repIndex === repeatCount
      setCurrentRepetition(repIndex)
      setStatus(isFinal ? 'FINAL_REPETITION' : 'PLAYING')
      isPlayingRef.current = true

      const textToSimulate = isFinal ? `${instruction} ${replayReminder}` : instruction
      simulateSpeech(repIndex, textToSimulate.length)
    },
    [instruction, repeatCount, replayReminder, isMuted, simulateSpeech, onComplete],
  )

  useEffect(() => {
    playRepetitionRef.current = playRepetition
  }, [playRepetition])

  // Restart the complete instruction loop from repetition 1
  const replay = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current)
      timerRef.current = null
    }
    setStatus('REPLAYING')
    setCurrentRepetition(1)
    setTimeout(() => {
      playRepetition(1)
    }, 80)
  }, [playRepetition])

  // Automatically start playback on mount or when instruction changes
  useEffect(() => {
    if (autoPlay && instruction && !isMuted) {
      const startTimer = setTimeout(() => {
        playRepetition(1)
      }, 350)
      return () => {
        clearTimeout(startTimer)
        if (timerRef.current) clearTimeout(timerRef.current)
      }
    } else if (isMuted) {
      stopPlayback()
    }
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current)
    }
  }, [instruction, autoPlay, isMuted, playRepetition, stopPlayback])

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
