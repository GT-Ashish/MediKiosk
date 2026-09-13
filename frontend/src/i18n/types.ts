/**
 * Schema definition for MediKiosk translations.
 * All supported languages (English, Hindi, Marathi, Bengali) must implement this schema.
 */

export interface TranslationSchema {
  common: {
    next: string
    back: string
    edit: string
    skip: string
    confirm: string
    retry: string
    submit: string
    cancel: string
    hearAgain: string
    mute: string
    unmute: string
    backToHome: string
    save: string
    done: string
    ready: string
    verified: string
  }

  header: {
    brandName: string
    tagline: string
  }

  page1_language: {
    title: string
    subtitle: string
    instruction: string
  }

  page2_consent: {
    title: string
    subtitle: string
    itemAnswers: string
    itemDocs: string
    itemHistory: string
    btnAgree: string
    btnDecline: string
    instruction: string
    modalTitle: string
    modalDesc: string
    modalBtnAgree: string
    modalBtnReturn: string
  }

  page3_identification: {
    title: string
    subtitle: string
    aadhaarTitle: string
    aadhaarDesc: string
    abhaTitle: string
    abhaDesc: string
    manualTitle: string
    manualDesc: string
    instruction: string
    modalTitleAadhaar: string
    modalTitleAbha: string
    modalTitleManual: string
    modalDemoNotice: string
    modalProfileTitle: string
    modalBtnConfirm: string
  }

  page4_visitReason: {
    title: string
    subtitle: string
    newProblemTitle: string
    newProblemDesc: string
    followUpTitle: string
    followUpDesc: string
    instruction: string
  }

  page5_complaint: {
    title: string
    subtitle: string
    instruction: string
    listening: string
    processing: string
    youSaid: string
    youEntered: string
    typePlaceholder: string
    startVoiceBtn: string
    switchToTypeBtn: string
    mockTranscript: string
  }

  page6_history: {
    subtitle: string
    dualInputHint: string
    orTapBelow: string
    skipNotSure: string
    listening: string
    processing: string
    youSaid: string
    youEntered: string
    typePlaceholder: string
    startVoiceBtn: string
    switchToTypeBtn: string
    instruction: string
    questions: {
      onset: {
        title: string
        subtitle: string
        options: {
          today: string
          yesterday: string
          fewDays: string
          moreWeek: string
        }
        mockAnswer: string
      }
      location: {
        title: string
        subtitle: string
        options: {
          upperAb: string
          lowerAb: string
          chest: string
          allOver: string
        }
        mockAnswer: string
      }
      severity: {
        title: string
        subtitle: string
        options: {
          mild: string
          moderate: string
          severe: string
          verySevere: string
        }
        mockAnswer: string
      }
      associated: {
        title: string
        subtitle: string
        options: {
          nausea: string
          fever: string
          lossAppetite: string
          none: string
        }
        mockAnswer: string
      }
    }
  }

  page7_documents: {
    title: string
    subtitle: string
    cardTitle: string
    cardSubtitle: string
    supportedFormats: string
    useScanner: string
    uploadPC: string
    uploadUSB: string
    scanningNotice: string
    usbNotice: string
    uploadedTitle: string
    instruction: string
  }

  page8_review: {
    title: string
    subtitle: string
    sectionPatientInfo: string
    sectionKeyPoints: string
    sectionDocs: string
    fieldName: string
    fieldAgeGender: string
    fieldVisitType: string
    fieldComplaint: string
    visitTypeNew: string
    visitTypeFollowUp: string
    editChiefComplaintNotice: string
    editKeyPointsTitle: string
    voiceOption: string
    typeOption: string
    disclaimer: string
    instruction: string
    // Modal & interaction strings
    editChiefComplaintModalTitle: string
    editChiefComplaintModalContinue: string
    editChooseMethodPrompt: string
    editChooseAnotherMethod: string
    noDocsAttached: string
    docPreviewLabel: string
    docPreviewCloseBtn: string
    docViewBtn: string
    // Follow-up specific
    sectionPreviousVisit: string
    fieldPreviousVisitDate: string
    fieldPreviousVisitDept: string
    fieldPreviousVisitComplaint: string
    fieldPreviousVisitDoctor: string
  }

  page9_confirmation: {
    title: string
    subtitle: string
    nextStepsTitle: string
    step1: string
    step2: string
    step3: string
    tokenLabel: string
    autoReturnMessage: string
    instruction: string
  }

  page10_followUp: {
    title: string
    subtitle: string
    consultingDoctor: string
    instruction: string
  }
}
