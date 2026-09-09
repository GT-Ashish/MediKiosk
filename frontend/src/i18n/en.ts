import type { TranslationSchema } from './types'

export const en: TranslationSchema = {
  common: {
    next: 'Next',
    back: 'Back',
    edit: 'Edit',
    skip: 'Skip / Not sure',
    confirm: 'Confirm',
    retry: 'Retry',
    submit: 'Submit',
    cancel: 'Cancel',
    hearAgain: 'Hear Again',
    mute: 'Mute',
    unmute: 'Unmute',
    backToHome: 'Back to Home',
    save: 'Save',
    done: 'Done',
    ready: 'Ready',
    verified: 'Verified',
  },

  header: {
    brandName: 'MediKiosk',
    tagline: 'Your Health, Our Priority.',
  },

  page1_language: {
    title: 'Welcome to MediKiosk',
    subtitle: 'Choose your preferred language',
    instruction: 'Welcome to MediKiosk. Please choose your preferred language.',
  },

  page2_consent: {
    title: 'Your Privacy Matters',
    subtitle: 'We need your permission to continue. We may collect:',
    itemAnswers: 'Your answers (voice or text)',
    itemDocs: 'Your medical documents',
    itemHistory: 'Your medical history',
    btnAgree: 'I Agree',
    btnDecline: "I Don't Agree",
    instruction:
      'Your privacy matters. Press the green button if you agree to share your answers, documents, and medical history with the doctor. Press the red button if you do not agree.',
    modalTitle: 'Consent Required',
    modalDesc:
      'To prepare your clinical history and documents for your doctor, MediKiosk requires your permission. Your data is stored securely and deleted after your OPD visit.',
    modalBtnAgree: 'I Understand, I Agree',
    modalBtnReturn: 'Return to Language Selection',
  },

  page3_identification: {
    title: "Let's identify you",
    subtitle: 'Choose a method to continue',
    aadhaarTitle: 'Aadhaar',
    aadhaarDesc: 'Use your Aadhaar to identify yourself',
    abhaTitle: 'ABHA ID',
    abhaDesc: 'Use your Ayushman Bharat Health ID',
    manualTitle: 'Enter Manually',
    manualDesc: 'Fill in your name and phone number',
    instruction:
      "Let's identify you. Choose whether to identify using Aadhaar, your ABHA ID, or enter your details manually.",
    modalTitleAadhaar: 'Aadhaar Verification',
    modalTitleAbha: 'ABHA ID Verification',
    modalTitleManual: 'Manual Patient Details',
    modalDemoNotice: 'Demo Simulation: No real Aadhaar or ABHA credentials are stored.',
    modalProfileTitle: 'Verified Patient Profile',
    modalBtnConfirm: 'Confirm & Next',
  },

  page4_visitReason: {
    title: 'What brings you here today?',
    subtitle: 'Choose the option that best applies',
    newProblemTitle: 'I have a health problem',
    newProblemDesc: 'Tell us about your symptoms or complaint',
    followUpTitle: 'Follow-up visit',
    followUpDesc: 'I have new reports or documents to add',
    instruction:
      "What brings you here today? Choose 'I have a health problem' to describe your symptoms, or choose 'Follow-up visit' if you are returning to add new reports or documents.",
  },

  page5_complaint: {
    title: 'Tell me about your problem',
    subtitle: "You can speak in your own words. You don't need to use medical terms.",
    instruction:
      "Tell me about your problem. You can speak in your own words. You don't need to use medical terms.",
    listening: "I'm listening...",
    processing: 'Processing your response...',
    youSaid: 'You said:',
    youEntered: 'You entered:',
    typePlaceholder: 'Or type your answer here...',
    startVoiceBtn: 'Speak Answer',
    switchToTypeBtn: 'Type Answer',
    mockTranscript: 'I have had stomach pain for three days.',
  },

  page6_history: {
    subtitle: 'You can speak or choose an option.',
    dualInputHint: 'Answer by speaking or choose an option below:',
    orTapBelow: 'Or choose an option below:',
    skipNotSure: 'Skip / Not sure',
    listening: "I'm listening...",
    processing: 'Processing your answer...',
    youSaid: 'You said:',
    youEntered: 'You entered:',
    typePlaceholder: 'Type custom answer...',
    startVoiceBtn: 'Speak Answer',
    switchToTypeBtn: 'Type Answer',
    instruction: 'Please answer the question by speaking or by tapping an option on the screen.',
    questions: {
      onset: {
        title: 'When did the pain start?',
        subtitle: 'You can speak or choose an option.',
        options: {
          today: 'Today',
          yesterday: 'Yesterday',
          fewDays: 'Few days ago',
          moreWeek: 'More than a week ago',
        },
        mockAnswer: 'Started 3 days ago',
      },
      location: {
        title: 'Where exactly does it hurt?',
        subtitle: 'Point or choose the area of discomfort.',
        options: {
          upperAb: 'Upper abdomen',
          lowerAb: 'Lower abdomen',
          chest: 'Chest area',
          allOver: 'All over stomach',
        },
        mockAnswer: 'Lower abdominal region',
      },
      severity: {
        title: 'How severe is the discomfort?',
        subtitle: 'Choose how intense it feels.',
        options: {
          mild: 'Mild (Manageable)',
          moderate: 'Moderate (Discomforting)',
          severe: 'Severe (Hard to bear)',
          verySevere: 'Very Severe',
        },
        mockAnswer: 'Moderate severity',
      },
      associated: {
        title: 'Do you have any other symptoms?',
        subtitle: 'Select any additional symptoms you feel.',
        options: {
          nausea: 'Nausea / Vomiting',
          fever: 'Fever / Chills',
          lossAppetite: 'Loss of Appetite',
          none: 'None of these',
        },
        mockAnswer: 'No vomiting, mild loss of appetite',
      },
    },
  },

  page7_documents: {
    title: 'Do you have any medical documents to add?',
    subtitle: 'You can upload prescriptions, lab reports, X-rays or discharge summaries.',
    cardTitle: 'Scan or upload documents',
    cardSubtitle: 'Select a method to upload existing physical or digital records',
    supportedFormats: 'Supported formats: PDF, JPG, PNG',
    useScanner: 'Use Scanner',
    uploadPC: 'Upload from PC',
    uploadUSB: 'Upload from USB',
    scanningNotice: 'Scanning document from kiosk feeder...',
    usbNotice: 'Reading documents from USB drive...',
    uploadedTitle: 'Uploaded Documents',
    instruction:
      'Do you have any medical documents to add? You can upload from your computer, scan prescriptions, or use a USB drive, or press Next to continue.',
  },

  page8_review: {
    title: "Here's what we understood",
    subtitle: 'Please review and confirm.',
    sectionPatientInfo: 'Your Information',
    sectionKeyPoints: 'Key Points from Conversation',
    sectionDocs: 'Uploaded Documents',
    fieldName: 'Name',
    fieldAgeGender: 'Age / Gender',
    fieldVisitType: 'Visit Type',
    fieldComplaint: 'Chief Complaint',
    visitTypeNew: 'New Problem',
    visitTypeFollowUp: 'Follow-up Visit',
    editChiefComplaintNotice:
      'Editing your chief complaint will restart the detailed questions so your doctor receives accurate information.',
    editKeyPointsTitle: 'Edit Conversation Key Point',
    voiceOption: 'Voice Input',
    typeOption: 'Type Input',
    disclaimer:
      'Notice: This structured summary is a draft prepared for your physician to review and edit during your consultation. It does not constitute a clinical diagnosis.',
    instruction:
      'Here is what we understood from your visit. Please review the details. You can make changes, or press Next to confirm.',
  },

  page9_confirmation: {
    title: 'Thank You!',
    subtitle: 'Your information has been recorded.',
    nextStepsTitle: 'What happens next?',
    step1: 'Your details and documents will be reviewed by the doctor.',
    step2: "You will be called on the OPD display screen when it's your turn.",
    step3: 'You can wait comfortably in the OPD waiting area.',
    tokenLabel: 'Your Token Number',
    autoReturnMessage: 'Returning to Home in {seconds} seconds',
    instruction:
      'Thank you! Your information has been recorded. Please take a seat in the waiting area until your number is called.',
  },

  page10_followUp: {
    title: 'Select your previous visit',
    subtitle: 'Choose the visit to which you want to add new reports.',
    consultingDoctor: 'Consulting Doctor',
    instruction:
      'Select your previous visit. Choose the visit to which you want to add new reports, then press Next.',
  },
}
