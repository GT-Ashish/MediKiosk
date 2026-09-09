import React, { createContext, useContext, useState, useCallback, useMemo, useEffect } from 'react'
import type {
  PageRoute,
  SupportedLanguage,
  PatientProfile,
  VisitType,
  MedicalDocument,
  PreviousVisitRecord,
  ClinicalSummaryDraft,
} from '../types'
import {
  SUPPORTED_LANGUAGES,
  DEFAULT_PATIENT,
  PREVIOUS_VISITS,
  INITIAL_DOCUMENTS,
  DEFAULT_CLINICAL_SUMMARY,
} from '../data/mockData'
import { getTranslations, type TranslationSchema } from '../i18n'

interface KioskContextType {
  // Navigation & View
  currentRoute: PageRoute
  appMode: 'kiosk' | 'doctor'
  routeHistory: PageRoute[]
  setAppMode: (mode: 'kiosk' | 'doctor') => void
  goTo: (route: PageRoute) => void
  goBack: () => void
  resetKiosk: () => void

  // Translations
  t: TranslationSchema

  // Mute Control (Resets per page)
  isMuted: boolean
  toggleMute: () => void

  // Patient Data State
  selectedLanguage: SupportedLanguage
  setSelectedLanguage: (lang: SupportedLanguage) => void
  consentGiven: boolean | null
  setConsentGiven: (agreed: boolean) => void
  patient: PatientProfile
  setPatient: (patient: PatientProfile) => void
  visitType: VisitType
  setVisitType: (type: VisitType) => void
  chiefComplaint: string
  setChiefComplaint: (complaint: string) => void
  historyAnswers: Record<string, string>
  setAnswerForQuestion: (questionId: string, questionText: string, answer: string) => void
  updateHistoryAnswer: (questionId: string, answer: string) => void
  editChiefComplaintFlow: () => void
  selectedPreviousVisit: PreviousVisitRecord | null
  setSelectedPreviousVisit: (visit: PreviousVisitRecord | null) => void
  documents: MedicalDocument[]
  addDocument: (doc: MedicalDocument) => void
  clinicalSummary: ClinicalSummaryDraft
  updateClinicalSummary: (summary: Partial<ClinicalSummaryDraft>) => void
  tokenNumber: string
}

const KioskContext = createContext<KioskContextType | null>(null)

export const KioskProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentRoute, setCurrentRoute] = useState<PageRoute>('language')
  const [routeHistory, setRouteHistory] = useState<PageRoute[]>(['language'])
  const [appMode, setAppMode] = useState<'kiosk' | 'doctor'>('kiosk')

  // Mute state - starts unmuted, resets on page transition
  const [isMuted, setIsMuted] = useState<boolean>(false)

  const [selectedLanguage, setSelectedLanguage] = useState<SupportedLanguage>(SUPPORTED_LANGUAGES[0])
  const [consentGiven, setConsentGiven] = useState<boolean | null>(null)
  const [patient, setPatient] = useState<PatientProfile>(DEFAULT_PATIENT)
  const [visitType, setVisitType] = useState<VisitType>('new_problem')
  const [chiefComplaint, setChiefComplaint] = useState<string>('')
  const [historyAnswers, setHistoryAnswers] = useState<Record<string, string>>({})
  const [selectedPreviousVisit, setSelectedPreviousVisit] = useState<PreviousVisitRecord | null>(PREVIOUS_VISITS[0])
  const [documents, setDocuments] = useState<MedicalDocument[]>(INITIAL_DOCUMENTS)
  const [clinicalSummary, setClinicalSummary] = useState<ClinicalSummaryDraft>(DEFAULT_CLINICAL_SUMMARY)
  const tokenNumber = 'A 102'

  // Dynamic translations based on selected language
  const t = useMemo(() => {
    return getTranslations(selectedLanguage.code)
  }, [selectedLanguage.code])

  // Toggle Mute for current page
  const toggleMute = useCallback(() => {
    setIsMuted((prev) => !prev)
  }, [])

  const goTo = useCallback((nextRoute: PageRoute) => {
    setIsMuted(false) // Reset mute state when navigating to next page
    setRouteHistory((prev) => [...prev, nextRoute])
    setCurrentRoute(nextRoute)
    window.scrollTo(0, 0)
  }, [])

  const goBack = useCallback(() => {
    setIsMuted(false) // Reset mute state on back
    setRouteHistory((prev) => {
      if (prev.length <= 1) return prev
      const newHistory = [...prev]
      newHistory.pop()
      const previous = newHistory[newHistory.length - 1]
      setCurrentRoute(previous)
      window.scrollTo(0, 0)
      return newHistory
    })
  }, [])

  // Invalidate detailed questions and return to Page 5 when editing chief complaint
  const editChiefComplaintFlow = useCallback(() => {
    setIsMuted(false)
    setHistoryAnswers({}) // Reset old detailed answers to avoid invalid history state
    setCurrentRoute('complaint')
    window.scrollTo(0, 0)
  }, [])

  const resetKiosk = useCallback(() => {
    setCurrentRoute('language')
    setRouteHistory(['language'])
    setSelectedLanguage(SUPPORTED_LANGUAGES[0])
    setConsentGiven(null)
    setVisitType('new_problem')
    setChiefComplaint('')
    setHistoryAnswers({})
    setSelectedPreviousVisit(PREVIOUS_VISITS[0])
    setDocuments(INITIAL_DOCUMENTS)
    setClinicalSummary(DEFAULT_CLINICAL_SUMMARY)
    setIsMuted(false)
    window.scrollTo(0, 0)
  }, [])

  const setAnswerForQuestion = useCallback((_questionId: string, _questionText: string, answer: string) => {
    setHistoryAnswers((prev) => ({
      ...prev,
      [_questionId]: answer,
    }))
  }, [])

  const updateHistoryAnswer = useCallback((questionId: string, answer: string) => {
    setHistoryAnswers((prev) => ({
      ...prev,
      [questionId]: answer,
    }))
  }, [])

  const addDocument = useCallback((doc: MedicalDocument) => {
    setDocuments((prev) => [doc, ...prev])
  }, [])

  const updateClinicalSummary = useCallback((summary: Partial<ClinicalSummaryDraft>) => {
    setClinicalSummary((prev) => ({ ...prev, ...summary }))
  }, [])

  // Sync initial chief complaint in selected language if empty
  useEffect(() => {
    if (!chiefComplaint) {
      setChiefComplaint(t.page5_complaint.mockTranscript)
    }
  }, [chiefComplaint, t.page5_complaint.mockTranscript])

  const value = useMemo(
    () => ({
      currentRoute,
      appMode,
      routeHistory,
      setAppMode,
      goTo,
      goBack,
      resetKiosk,
      t,
      isMuted,
      toggleMute,
      selectedLanguage,
      setSelectedLanguage,
      consentGiven,
      setConsentGiven,
      patient,
      setPatient,
      visitType,
      setVisitType,
      chiefComplaint,
      setChiefComplaint,
      historyAnswers,
      setAnswerForQuestion,
      updateHistoryAnswer,
      editChiefComplaintFlow,
      selectedPreviousVisit,
      setSelectedPreviousVisit,
      documents,
      addDocument,
      clinicalSummary,
      updateClinicalSummary,
      tokenNumber,
    }),
    [
      currentRoute,
      appMode,
      routeHistory,
      goTo,
      goBack,
      resetKiosk,
      t,
      isMuted,
      toggleMute,
      selectedLanguage,
      consentGiven,
      patient,
      visitType,
      chiefComplaint,
      historyAnswers,
      setAnswerForQuestion,
      updateHistoryAnswer,
      editChiefComplaintFlow,
      selectedPreviousVisit,
      documents,
      addDocument,
      clinicalSummary,
      updateClinicalSummary,
      tokenNumber,
    ],
  )

  return <KioskContext.Provider value={value}>{children}</KioskContext.Provider>
}

export function useKiosk(): KioskContextType {
  const context = useContext(KioskContext)
  if (!context) {
    throw new Error('useKiosk must be used within a KioskProvider')
  }
  return context
}
