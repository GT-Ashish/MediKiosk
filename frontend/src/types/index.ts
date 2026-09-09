/**
 * MediKiosk Domain Types and State Models.
 */

export type PageRoute =
  | 'language'        // Page 1
  | 'consent'         // Page 2
  | 'identification'  // Page 3
  | 'visit_reason'    // Page 4
  | 'complaint'       // Page 5 (Branch A)
  | 'history_taking'  // Page 6 (Branch A)
  | 'documents'       // Page 7
  | 'review'          // Page 8
  | 'confirmation'    // Page 9
  | 'follow_up'       // Page 10 (Branch B)

export interface SupportedLanguage {
  code: string
  name: string
  nativeName: string
  badgeText: string
  badgeBg: string
  badgeTextColor: string
}

export type IdentificationMethod = 'aadhaar' | 'abha' | 'manual'

export interface PatientProfile {
  id: string
  name: string
  age: number
  gender: string
  idMethod: IdentificationMethod
  maskedId: string
  phone: string
}

export type VisitType = 'new_problem' | 'follow_up'

export interface QuestionOption {
  id: string
  label: string
}

export interface HistoryQuestion {
  id: string
  title: string
  subtitle: string
  options: QuestionOption[]
  defaultAnswer: string
}

export interface HistoryAnswer {
  questionId: string
  questionText: string
  selectedAnswer: string
}

export interface MedicalDocument {
  id: string
  title: string
  type: 'prescription' | 'lab_report' | 'xray' | 'discharge_summary'
  date: string
  size: string
  status: 'verified' | 'uploaded'
}

export interface PreviousVisitRecord {
  id: string
  date: string
  complaint: string
  doctor: string
  department: string
}

export interface ClinicalSummaryDraft {
  patientName: string
  ageGender: string
  visitType: string
  chiefComplaint: string
  keyPoints: string[]
  uploadedDocuments: MedicalDocument[]
  reviewStatus: 'draft' | 'confirmed' | 'rejected'
  physicianNotes?: string
}

export interface DoctorQueuePatient {
  tokenNumber: string
  patientName: string
  ageGender: string
  visitType: string
  complaint: string
  arrivalTime: string
  status: 'Waiting' | 'In Consultation' | 'Completed'
  isRedFlag: boolean
  redFlagReason?: string
  historySummary: ClinicalSummaryDraft
  previousVisits: PreviousVisitRecord[]
}

export type InstructionStatus =
  | 'IDLE'
  | 'PLAYING'
  | 'FINAL_REPETITION'
  | 'COMPLETED'
  | 'REPLAYING'

export type VoiceListeningStatus =
  | 'IDLE'
  | 'LISTENING'
  | 'PROCESSING'
  | 'SUCCESS'
  | 'RETRY'
  | 'FALLBACK'
