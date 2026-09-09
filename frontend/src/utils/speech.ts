// Centralized Web Speech API utilities for MediKiosk (TTS & Speech Recognition)
// Handles Chrome's known speechSynthesis bugs:
//  1. onvoiceschanged is async — voices are often empty on first call
//  2. Chrome pauses speechSynthesis after ~15s unless periodically resumed
//  3. speechSynthesis.cancel() then speak() immediately can sometimes silently fail

export function getSpeechLanguageTag(langCode: string): string {
  switch (langCode) {
    case 'hi':
      return 'hi-IN'
    case 'mr':
      return 'mr-IN'
    case 'bn':
      return 'bn-IN'
    case 'en':
    default:
      return 'en-IN'
  }
}

// Cached voices loaded asynchronously from window.speechSynthesis
let cachedVoices: SpeechSynthesisVoice[] = []
let voicesLoaded = false
const voiceLoadCallbacks: Array<() => void> = []

function loadVoices(): SpeechSynthesisVoice[] {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
    return []
  }
  const voices = window.speechSynthesis.getVoices()
  if (voices && voices.length > 0) {
    cachedVoices = voices
    if (!voicesLoaded) {
      voicesLoaded = true
      // Notify any pending speak() calls
      voiceLoadCallbacks.splice(0).forEach((cb) => cb())
    }
  }
  return cachedVoices
}

// Initialize voices and handle voiceschanged event
if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
  loadVoices()
  window.speechSynthesis.addEventListener('voiceschanged', () => {
    loadVoices()
  })
}

/**
 * Finds the most suitable SpeechSynthesisVoice for the requested language.
 * 1. Exact match for target language code (e.g. hi-IN)
 * 2. Primary language family match (e.g. hi)
 * 3. Fallback to default/first available voice
 */
function selectBestVoice(langTag: string, langCode: string): SpeechSynthesisVoice | undefined {
  const voices = loadVoices()
  if (!voices || voices.length === 0) return undefined

  const normalizedTag = langTag.toLowerCase().replace('_', '-')
  const primaryLang = langCode.toLowerCase()

  // 1. Exact tag match (e.g. hi-IN)
  const exactMatch = voices.find(
    (v) => v.lang.toLowerCase().replace('_', '-') === normalizedTag
  )
  if (exactMatch) return exactMatch

  // 2. Primary language prefix match (e.g. hi or mr)
  const prefixMatch = voices.find(
    (v) => v.lang.toLowerCase().startsWith(primaryLang)
  )
  if (prefixMatch) return prefixMatch

  // 3. Indian English / Indian regional voices if requesting Indian locale
  if (primaryLang === 'mr' || primaryLang === 'bn' || primaryLang === 'hi') {
    const hindiFallback = voices.find((v) => v.lang.toLowerCase().startsWith('hi'))
    if (hindiFallback) return hindiFallback
    const indianEn = voices.find((v) => v.lang.toLowerCase().includes('in'))
    if (indianEn) return indianEn
  }

  // 4. Default voice or first voice
  return voices.find((v) => v.default) || voices[0]
}

export interface SpeakTextOptions {
  onEnd?: () => void
  onError?: (error: any) => void
  rate?: number
  pitch?: number
}

/**
 * Speaks the given text using browser-native SpeechSynthesis.
 * Cancels existing speech, selects the best voice, and executes with a calm clinical cadence.
 * Handles Chrome's ~15s pause bug via a keep-alive interval.
 * Returns a cleanup/stop function.
 */
export function speakText(
  text: string,
  langCode: string,
  options: SpeakTextOptions = {}
): () => void {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
    options.onEnd?.()
    return () => {}
  }

  if (!text || text.trim() === '') {
    options.onEnd?.()
    return () => {}
  }

  let isCancelled = false
  let keepAliveInterval: ReturnType<typeof setInterval> | null = null

  const doSpeak = () => {
    if (isCancelled) return

    // Cancel any active speech before starting a new utterance
    try {
      window.speechSynthesis.cancel()
    } catch {
      // ignore
    }

    const langTag = getSpeechLanguageTag(langCode)
    const utterance = new SpeechSynthesisUtterance(text)

    utterance.lang = langTag
    utterance.rate = options.rate ?? 0.92 // Calm clinical rate
    utterance.pitch = options.pitch ?? 1.0

    const voice = selectBestVoice(langTag, langCode)
    if (voice) {
      utterance.voice = voice
    }

    let hasEnded = false

    const cleanup = () => {
      if (keepAliveInterval !== null) {
        clearInterval(keepAliveInterval)
        keepAliveInterval = null
      }
    }

    const handleEnd = () => {
      if (hasEnded) return
      hasEnded = true
      cleanup()
      if (!isCancelled) {
        options.onEnd?.()
      }
    }

    const handleError = (e: any) => {
      if (hasEnded) return
      hasEnded = true
      cleanup()
      // 'canceled' / 'interrupted' is normal when user navigates or replays
      if (e?.error !== 'canceled' && e?.error !== 'interrupted' && !isCancelled) {
        console.warn('[TTS Warning] Speech error:', e?.error || e)
      }
      if (!isCancelled) {
        options.onError?.(e)
      }
    }

    utterance.onend = handleEnd
    utterance.onerror = handleError

    try {
      window.speechSynthesis.speak(utterance)

      // Chrome bug fix: speechSynthesis pauses after ~15 seconds.
      // Calling resume() every 10s prevents premature pause.
      keepAliveInterval = setInterval(() => {
        if (window.speechSynthesis.speaking && !window.speechSynthesis.paused) {
          // Still speaking normally — no action needed
          return
        }
        if (window.speechSynthesis.paused) {
          // Chrome paused it — resume immediately
          window.speechSynthesis.resume()
        } else if (!window.speechSynthesis.speaking) {
          // Utterance finished — clear the interval
          cleanup()
        }
      }, 5000)
    } catch (err) {
      console.warn('[TTS Warning] Failed to start speak:', err)
      cleanup()
      handleError(err)
    }
  }

  // If voices aren't available yet, wait for them (Chrome async voice loading)
  if (cachedVoices.length === 0 && !voicesLoaded) {
    // Wait up to 2 seconds for voices, then proceed anyway
    let resolved = false
    const timeout = setTimeout(() => {
      if (!resolved && !isCancelled) {
        resolved = true
        doSpeak()
      }
    }, 2000)

    voiceLoadCallbacks.push(() => {
      if (!resolved && !isCancelled) {
        resolved = true
        clearTimeout(timeout)
        doSpeak()
      }
    })
  } else {
    // Voices already available — speak immediately
    // Small delay after cancel() to prevent Chrome from silently dropping the utterance
    setTimeout(doSpeak, 50)
  }

  // Return safe cleanup/stop function
  return () => {
    isCancelled = true
    if (keepAliveInterval !== null) {
      clearInterval(keepAliveInterval)
      keepAliveInterval = null
    }
    try {
      window.speechSynthesis.cancel()
    } catch {
      // ignore
    }
  }
}

/**
 * Safely cancels any ongoing browser speech synthesis.
 */
export function stopSpeaking(): void {
  if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
    try {
      window.speechSynthesis.cancel()
    } catch {
      // ignore
    }
  }
}

export interface SpeechRecognitionCallbacks {
  onResult: (transcript: string, isFinal: boolean) => void
  onEnd: (finalTranscript: string) => void
  onError: (error: any) => void
}

export interface SpeechRecognitionControls {
  stop: () => void
  abort: () => void
}

/**
 * Starts browser-native SpeechRecognition (Chrome / Edge).
 * Returns control functions (stop, abort) or null if not supported.
 */
export function startSpeechRecognition(
  langCode: string,
  callbacks: SpeechRecognitionCallbacks
): SpeechRecognitionControls | null {
  if (typeof window === 'undefined') return null

  const SpeechRecognitionClass =
    (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition

  if (!SpeechRecognitionClass) {
    return null
  }

  try {
    const recognition = new SpeechRecognitionClass()
    const langTag = getSpeechLanguageTag(langCode)

    recognition.lang = langTag
    recognition.continuous = false
    recognition.interimResults = true
    recognition.maxAlternatives = 1

    let finalTranscript = ''
    let isFinished = false

    recognition.onresult = (event: any) => {
      let interimTranscript = ''
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        const result = event.results[i]
        const text = result[0]?.transcript || ''
        if (result.isFinal) {
          finalTranscript += text
        } else {
          interimTranscript += text
        }
      }

      const activeText = finalTranscript || interimTranscript
      const isFinal = Boolean(finalTranscript && !interimTranscript)
      callbacks.onResult(activeText.trim(), isFinal)
    }

    recognition.onend = () => {
      if (isFinished) return
      isFinished = true
      callbacks.onEnd(finalTranscript.trim())
    }

    recognition.onerror = (event: any) => {
      if (isFinished) return
      isFinished = true
      callbacks.onError(event)
    }

    recognition.start()

    return {
      stop: () => {
        try {
          recognition.stop()
        } catch {
          // ignore
        }
      },
      abort: () => {
        isFinished = true
        try {
          recognition.abort()
        } catch {
          // ignore
        }
      },
    }
  } catch (err) {
    console.warn('[SpeechRecognition] Could not instantiate:', err)
    return null
  }
}
