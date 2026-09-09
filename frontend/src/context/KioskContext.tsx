import React, { createContext, useContext, useState, useCallback, useMemo } from 'react'
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

interface KioskContextType {
  // Navigation & View
  currentRoute: PageRoute
  appMode: 'kiosk' | 'doctor'
  routeHistory: PageRoute[]
  setAppMode: (mode: 'kiosk' | 'doctor') => void
  goTo: (route: PageRoute) => void
  goBack: () => void
  resetKiosk: () => void

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

  const [selectedLanguage, setSelectedLanguage] = useState<SupportedLanguage>(SUPPORTED_LANGUAGES[0])
  const [consentGiven, setConsentGiven] = useState<boolean | null>(null)
  const [patient, setPatient] = useState<PatientProfile>(DEFAULT_PATIENT)
  const [visitType, setVisitType] = useState<VisitType>('new_problem')
  const [chiefComplaint, setChiefComplaint] = useState<string>('I have had stomach pain for three days.')
  const [historyAnswers, setHistoryAnswers] = useState<Record<string, string>>({
    onset: 'Few days ago (3 days)',
    location: 'Lower abdominal region',
    severity: 'Moderate severity',
    associated: 'No vomiting, mild loss of appetite',
  })
  const [selectedPreviousVisit, setSelectedPreviousVisit] = useState<PreviousVisitRecord | null>(PREVIOUS_VISITS[0])
  const [documents, setDocuments] = useState<MedicalDocument[]>(INITIAL_DOCUMENTS)
  const [clinicalSummary, setClinicalSummary] = useState<ClinicalSummaryDraft>(DEFAULT_CLINICAL_SUMMARY)
  const tokenNumber = 'A 102'

  const goTo = useCallback((nextRoute: PageRoute) => {
    setRouteHistory((prev) => [...prev, nextRoute])
    setCurrentRoute(nextRoute)
    window.scrollTo(0, 0)
  }, [])

  const goBack = useCallback(() => {
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

  const resetKiosk = useCallback(() => {
    setCurrentRoute('language')
    setRouteHistory(['language'])
    setSelectedLanguage(SUPPORTED_LANGUAGES[0])
    setConsentGiven(null)
    setVisitType('new_problem')
    setChiefComplaint('I have had stomach pain for three days.')
    setHistoryAnswers({
      onset: 'Few days ago (3 days)',
      location: 'Lower abdominal region',
      severity: 'Moderate severity',
      associated: 'No vomiting, mild loss of appetite',
    })
    setSelectedPreviousVisit(PREVIOUS_VISITS[0])
    setDocuments(INITIAL_DOCUMENTS)
    setClinicalSummary(DEFAULT_CLINICAL_SUMMARY)
    window.scrollTo(0, 0)
  }, [])

  const setAnswerForQuestion = useCallback((_questionId: string, _questionText: string, answer: string) => {
    setHistoryAnswers((prev) => ({
      ...prev,
      [_questionId]: answer,
    }))
  }, [])

  const addDocument = useCallback((doc: MedicalDocument) => {
    setDocuments((prev) => [doc, ...prev])
  }, [])

  const updateClinicalSummary = useCallback((summary: Partial<ClinicalSummaryDraft>) => {
    setClinicalSummary((prev) => ({ ...prev, ...summary }))
  }, [])

  const value = useMemo(
    () => ({
      currentRoute,
      appMode,
      routeHistory,
      setAppMode,
      goTo,
      goBack,
      resetKiosk,
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
      selectedLanguage,
      consentGiven,
      patient,
      visitType,
      chiefComplaint,
      historyAnswers,
      setAnswerForQuestion,
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
