import { useState, useEffect, useRef, useCallback } from 'react'
import type { VoiceListeningStatus } from '../types'

interface UseVoiceInteractionProps {
  autoStart?: boolean
  defaultMockTranscript?: string
  onSuccess?: (transcript: string) => void
  maxRetries?: number
}

interface UseVoiceInteractionReturn {
  status: VoiceListeningStatus
  transcript: string
  retryCount: number
  isListening: boolean
  showFallback: boolean
  statusMessage: string
  startListening: () => void
  stopListening: () => void
  triggerManualSuccess: (text: string) => void
  triggerRetry: () => void
  switchToFallback: () => void
}

export function useVoiceInteraction({
  autoStart = true,
  defaultMockTranscript = 'I have had stomach pain for three days.',
  onSuccess,
  maxRetries = 2,
}: UseVoiceInteractionProps): UseVoiceInteractionReturn {
  const [status, setStatus] = useState<VoiceListeningStatus>('IDLE')
  const [transcript, setTranscript] = useState<string>('')
  const [retryCount, setRetryCount] = useState<number>(0)
  const [showFallback, setShowFallback] = useState<boolean>(false)
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  const clearTimers = useCallback(() => {
    if (timerRef.current) {
      clearTimeout(timerRef.current)
      timerRef.current = null
    }
  }, [])

  const startListening = useCallback(() => {
    clearTimers()
    setStatus('LISTENING')
    setTranscript('')

    // Simulate listening duration: 3.5 seconds of listening, then processing
    timerRef.current = setTimeout(() => {
      setStatus('PROCESSING')

      // 1.5 seconds processing
      timerRef.current = setTimeout(() => {
        const text = defaultMockTranscript
        setTranscript(text)
        setStatus('SUCCESS')
        if (onSuccess) {
          onSuccess(text)
        }
      }, 1400)
    }, 3600)
  }, [clearTimers, defaultMockTranscript, onSuccess])

  const stopListening = useCallback(() => {
    clearTimers()
    setStatus('IDLE')
  }, [clearTimers])

  const triggerManualSuccess = useCallback(
    (text: string) => {
      clearTimers()
      setTranscript(text)
      setStatus('SUCCESS')
      if (onSuccess) {
        onSuccess(text)
      }
    },
    [clearTimers, onSuccess],
  )

  const switchToFallback = useCallback(() => {
    clearTimers()
    setStatus('FALLBACK')
    setShowFallback(true)
  }, [clearTimers])

  // Handle retry when speech is not understood
  const triggerRetry = useCallback(() => {
    clearTimers()
    if (retryCount >= maxRetries) {
      switchToFallback()
      return
    }

    setRetryCount((prev) => prev + 1)
    setStatus('RETRY')

    // After brief retry message, restart listening
    timerRef.current = setTimeout(() => {
      startListening()
    }, 2000)
  }, [clearTimers, retryCount, maxRetries, switchToFallback, startListening])

  // Auto start on mount
  useEffect(() => {
    if (autoStart) {
      // Delay auto-start slightly so the user first hears/sees the page prompt
      const delay = setTimeout(() => {
        startListening()
      }, 1000)
      return () => {
        clearTimeout(delay)
        clearTimers()
      }
    }
    return () => {
      clearTimers()
    }
  }, [autoStart, startListening, clearTimers])

  let statusMessage = "I'm listening..."
  if (status === 'PROCESSING') statusMessage = 'Processing your voice...'
  if (status === 'SUCCESS') statusMessage = 'Understood'
  if (status === 'RETRY') statusMessage = "I couldn't hear your answer. Please speak again."
  if (status === 'FALLBACK') statusMessage = 'Touch or type your response below'

  return {
    status,
    transcript,
    retryCount,
    isListening: status === 'LISTENING',
    showFallback,
    statusMessage,
    startListening,
    stopListening,
    triggerManualSuccess,
    triggerRetry,
    switchToFallback,
  }
}

