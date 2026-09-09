import { en } from './en'
import { hi } from './hi'
import { mr } from './mr'
import { bn } from './bn'
import type { TranslationSchema } from './types'

export type { TranslationSchema }

export const TRANSLATIONS: Record<string, TranslationSchema> = {
  en,
  hi,
  mr,
  bn,
}

export const REPLAY_REMINDERS: Record<string, string> = {
  en: 'To hear this instruction again, press the blue Hear Again button at the bottom.',
  hi: 'इस निर्देश को फिर से सुनने के लिए, नीचे दिए गए नीले फिर से सुनें बटन को दबाएं।',
  mr: 'ही सूचना पुन्हा ऐकण्यासाठी, खालील निळ्या पुन्हा ऐका बटणावर दाबा.',
  bn: 'এই নির্দেশটি আবার শুনতে, নিচে দেওয়া নীল আবার শুনুন বোতামটি টিপুন।',
}

export function getTranslations(langCode: string): TranslationSchema {
  return TRANSLATIONS[langCode] || TRANSLATIONS.en
}

export function getReplayReminder(langCode: string): string {
  return REPLAY_REMINDERS[langCode] || REPLAY_REMINDERS.en
}
