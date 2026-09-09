import type {
  SupportedLanguage,
  PatientProfile,
  HistoryQuestion,
  PreviousVisitRecord,
  MedicalDocument,
  ClinicalSummaryDraft,
  DoctorQueuePatient,
} from '../types'

export const SUPPORTED_LANGUAGES: SupportedLanguage[] = [
  {
    code: 'en',
    name: 'English',
    nativeName: 'English',
    badgeText: 'EN',
    badgeBg: '#DBEAFE',
    badgeTextColor: '#1E40AF',
  },
  {
    code: 'hi',
    name: 'Hindi',
    nativeName: 'हिंदी',
    badgeText: 'हि',
    badgeBg: '#DCFCE7',
    badgeTextColor: '#166534',
  },
  {
    code: 'mr',
    name: 'Marathi',
    nativeName: 'मराठी',
    badgeText: 'म',
    badgeBg: '#FEF3C7',
    badgeTextColor: '#92400E',
  },
  {
    code: 'bn',
    name: 'Bengali',
    nativeName: 'বাংলা',
    badgeText: 'বা',
    badgeBg: '#E0E7FF',
    badgeTextColor: '#3730A3',
  },
]

export const DEFAULT_PATIENT: PatientProfile = {
  id: 'PT-2026-9810',
  name: 'Rahul Sharma',
  age: 32,
  gender: 'Male',
  idMethod: 'aadhaar',
  maskedId: 'XXXX-XXXX-4821',
  phone: '+91 98765 43210',
}

export const HISTORY_QUESTIONS: HistoryQuestion[] = [
  {
    id: 'onset',
    title: 'When did the pain start?',
    subtitle: 'You can speak or choose an option.',
    options: [
      { id: 'today', label: 'Today' },
      { id: 'yesterday', label: 'Yesterday' },
      { id: 'few_days', label: 'Few days ago' },
      { id: 'more_week', label: 'More than a week ago' },
    ],
    defaultAnswer: 'Few days ago (3 days)',
  },
  {
    id: 'location',
    title: 'Where exactly does it hurt?',
    subtitle: 'Point or choose the area of discomfort.',
    options: [
      { id: 'upper_ab', label: 'Upper abdomen' },
      { id: 'lower_ab', label: 'Lower abdomen' },
      { id: 'chest', label: 'Chest area' },
      { id: 'all_over', label: 'All over stomach' },
    ],
    defaultAnswer: 'Lower abdominal region',
  },
  {
    id: 'severity',
    title: 'How severe is the discomfort?',
    subtitle: 'Choose how intense it feels.',
    options: [
      { id: 'mild', label: 'Mild (Manageable)' },
      { id: 'moderate', label: 'Moderate (Discomforting)' },
      { id: 'severe', label: 'Severe (Hard to bear)' },
      { id: 'unbearable', label: 'Very Severe' },
    ],
    defaultAnswer: 'Moderate severity',
  },
  {
    id: 'associated',
    title: 'Do you have any other symptoms?',
    subtitle: 'Select any additional symptoms you feel.',
    options: [
      { id: 'nausea', label: 'Nausea / Vomiting' },
      { id: 'fever', label: 'Fever / Chills' },
      { id: 'loss_appetite', label: 'Loss of Appetite' },
      { id: 'none', label: 'None of these' },
    ],
    defaultAnswer: 'No vomiting, mild loss of appetite',
  },
]

export const PREVIOUS_VISITS: PreviousVisitRecord[] = [
  {
    id: 'v-1',
    date: '15 Aug 2026',
    complaint: 'Abdominal pain',
    doctor: 'Dr. S. Mehta',
    department: 'Gastroenterology',
  },
  {
    id: 'v-2',
    date: '12 Feb 2026',
    complaint: 'Fever & chills',
    doctor: 'Dr. R. Kapoor',
    department: 'General Medicine',
  },
  {
    id: 'v-3',
    date: '3 Nov 2025',
    complaint: 'General check-up',
    doctor: 'Dr. A. Iyer',
    department: 'Internal Medicine',
  },
]

export const INITIAL_DOCUMENTS: MedicalDocument[] = [
  {
    id: 'doc-1',
    title: 'Lab Report — Jan 2026.pdf',
    type: 'lab_report',
    date: '18 Jan 2026',
    size: '1.4 MB',
    status: 'verified',
  },
  {
    id: 'doc-2',
    title: 'Prescription — Dec 2025.jpg',
    type: 'prescription',
    date: '22 Dec 2025',
    size: '820 KB',
    status: 'verified',
  },
]

export const DEFAULT_CLINICAL_SUMMARY: ClinicalSummaryDraft = {
  patientName: 'Rahul Sharma',
  ageGender: '32 years / Male',
  visitType: 'New Problem',
  chiefComplaint: 'Abdominal pain for 3 days',
  keyPoints: [
    'Pain started gradually 3 days ago',
    'Located in lower abdominal region',
    'Moderate severity, cramping in nature',
    'No vomiting, mild loss of appetite',
    'No known drug allergies reported',
  ],
  uploadedDocuments: [
    {
      id: 'doc-1',
      title: 'Lab Report — Jan 2026.pdf',
      type: 'lab_report',
      date: '18 Jan 2026',
      size: '1.4 MB',
      status: 'verified',
    },
  ],
  reviewStatus: 'draft',
}

export const MOCK_DOCTOR_QUEUE: DoctorQueuePatient[] = [
  {
    tokenNumber: 'A 101',
    patientName: 'Sunita Verma',
    ageGender: '58 years / Female',
    visitType: 'Follow-up',
    complaint: 'Hypertension follow-up & BP review',
    arrivalTime: '09:45 AM',
    status: 'Completed',
    isRedFlag: false,
    historySummary: {
      patientName: 'Sunita Verma',
      ageGender: '58 years / Female',
      visitType: 'Follow-up',
      chiefComplaint: 'Routine BP check, mild morning headaches',
      keyPoints: [
        'History of hypertension for 6 years on Amlodipine 5mg',
        'Reports morning headaches since 4 days',
        'Compliance with medication confirmed',
      ],
      uploadedDocuments: [],
      reviewStatus: 'confirmed',
    },
    previousVisits: [
      {
        id: 'sv-1',
        date: '10 Jun 2026',
        complaint: 'BP titration',
        doctor: 'Dr. V. Rao',
        department: 'Cardiology',
      },
    ],
  },
  {
    tokenNumber: 'A 102',
    patientName: 'Rahul Sharma',
    ageGender: '32 years / Male',
    visitType: 'New Problem',
    complaint: 'Abdominal pain for 3 days',
    arrivalTime: '10:20 AM',
    status: 'Waiting',
    isRedFlag: false,
    historySummary: DEFAULT_CLINICAL_SUMMARY,
    previousVisits: PREVIOUS_VISITS,
  },
  {
    tokenNumber: 'A 103',
    patientName: 'Anil Deshmukh',
    ageGender: '67 years / Male',
    visitType: 'New Problem',
    complaint: 'Acute chest tightness & shortness of breath',
    arrivalTime: '10:32 AM',
    status: 'Waiting',
    isRedFlag: true,
    redFlagReason: 'Emergency Red-Flag: Acute chest discomfort with dyspnea. Prioritize immediate triage.',
    historySummary: {
      patientName: 'Anil Deshmukh',
      ageGender: '67 years / Male',
      visitType: 'New Problem',
      chiefComplaint: 'Chest heaviness radiating to left shoulder',
      keyPoints: [
        'Onset 2 hours ago while resting',
        'Associated with diaphoresis and breathlessness',
        'PRIORITY RED FLAG: Immediate ECG & clinical assessment required',
      ],
      uploadedDocuments: [],
      reviewStatus: 'draft',
    },
    previousVisits: [],
  },
]
