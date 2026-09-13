import type { TranslationSchema } from './types'

export const bn: TranslationSchema = {
  common: {
    next: 'পরবর্তী',
    back: 'পূর্ববর্তী',
    edit: 'সম্পাদনা',
    skip: 'এড়িয়ে যান / নিশ্চিত নন',
    confirm: 'নিশ্চিত করুন',
    retry: 'আবার বলুন',
    submit: 'জমা দিন',
    cancel: 'বাতিল',
    hearAgain: 'আবার শুনুন',
    mute: 'শব্দ বন্ধ (Mute)',
    unmute: 'শব্দ চালু করুন',
    backToHome: 'হোম পেজে যান',
    save: 'সংরক্ষণ',
    done: 'সম্পন্ন',
    ready: 'প্রস্তুত',
    verified: 'যাচাইকৃত',
  },

  header: {
    brandName: 'MediKiosk (মেডিকিয়স্ক)',
    tagline: 'আপনার স্বাস্থ্য, আমাদের অগ্রাধিকার।',
  },

  page1_language: {
    title: 'মেডিকিয়স্কে স্বাগতম',
    subtitle: 'আপনার পছন্দের ভাষা নির্বাচন করুন',
    instruction: 'মেডিকিয়স্কে স্বাগতম। অনুগ্রহ করে আপনার পছন্দের ভাষা নির্বাচন করুন।',
  },

  page2_consent: {
    title: 'আপনার গোপনীয়তা অত্যন্ত গুরুত্বপূর্ণ',
    subtitle: 'এগিয়ে যেতে আমাদের আপনার সম্মতি প্রয়োজন। আমরা সংগ্রহ করতে পারি:',
    itemAnswers: 'আপনার উত্তরসমূহ (ভয়েস বা টাইপ করে)',
    itemDocs: 'আপনার পূর্ববর্তী মেডিকেল নথিপত্র',
    itemHistory: 'আপনার পূর্ববর্তী চিকিৎসার ইতিহাস',
    btnAgree: 'আমি সম্মত',
    btnDecline: 'আমি সম্মত নই',
    instruction:
      'আপনার গোপনীয়তা গুরুত্বপূর্ণ। ডাক্তারের সাথে তথ্য শেয়ার করতে সম্মত হলে সবুজ বোতাম টিপুন। সম্মত না হলে লাল বোতাম টিপুন।',
    modalTitle: 'সম্মতি প্রয়োজন',
    modalDesc:
      'ডাক্তারের জন্য তথ্য প্রস্তুত করতে মেডিকিয়স্কের আপনার অনুমতি প্রয়োজন। আপনার তথ্য সম্পূর্ণ সুরক্ষিত থাকে এবং পরামর্শের পর মুছে দেওয়া হয়।',
    modalBtnAgree: 'আমি বুঝতে পেরেছি, আমি সম্মত',
    modalBtnReturn: 'ভাষা নির্বাচনে ফিরে যান',
  },

  page3_identification: {
    title: 'আপনার পরিচয় নিশ্চিত করুন',
    subtitle: 'চালিয়ে যেতে একটি বিকল্প নির্বাচন করুন',
    aadhaarTitle: 'আধার কার্ড',
    aadhaarDesc: 'পরিচয়ের জন্য আপনার আধার ব্যবহার করুন',
    abhaTitle: 'আভা আইডি (ABHA ID)',
    abhaDesc: 'আপনার আয়ুষ্মান ভারত হেলথ আইডি ব্যবহার করুন',
    manualTitle: 'নিজে তথ্য দিন',
    manualDesc: 'আপনার নাম এবং মোবাইল নম্বর লিখুন',
    instruction:
      'আপনার পরিচয় নিশ্চিত করুন। আধার, আভা আইডি বা নিজে তথ্য পূরণ করার বিকল্প বেছে নিন।',
    modalTitleAadhaar: 'আধার যাচাইকরণ',
    modalTitleAbha: 'আভা আইডি যাচাইকরণ',
    modalTitleManual: 'রোগীর বিবরণ',
    modalDemoNotice: 'ডেমো সিমুলেশন: কোনো আসল আধার বা আভা ডেটা সংরক্ষণ করা হয় না।',
    modalProfileTitle: 'যাচাইকৃত রোগীর প্রোফাইল',
    modalBtnConfirm: 'নিশ্চিত করে এগিয়ে যান',
  },

  page4_visitReason: {
    title: 'আজ আসার কারণ কি?',
    subtitle: 'সবচেয়ে উপযুক্ত বিকল্পটি বেছে নিন',
    newProblemTitle: 'আমার স্বাস্থ্যের সমস্যা আছে',
    newProblemDesc: 'আপনার উপসর্গ বা সমস্যা সম্পর্কে বলুন',
    followUpTitle: 'ফলো-আপ ভিজিট',
    followUpDesc: 'আমার কাছে নতুন রিপোর্ট বা নথি যোগ করার আছে',
    instruction:
      'আজ আসার কারণ কি? নতুন অসুস্থতার জন্য স্বাস্থ্য সমস্যা বেছে নিন, অথবা পুরোনো রিপোর্ট যুক্ত করতে ফলো-আপ বেছে নিন।',
  },

  page5_complaint: {
    title: 'আপনার সমস্যা সম্পর্কে বলুন',
    subtitle: 'আপনি স্বাভাবিক ভাষায় কথা বলতে পারেন। কোনো ডাক্তারি শব্দের প্রয়োজন নেই।',
    instruction:
      'আপনার সমস্যা সম্পর্কে বলুন। আপনি সহজ ভাষায় বলতে পারেন। ডাক্তারি শব্দের প্রয়োজন নেই।',
    listening: 'আমি শুনছি...',
    processing: 'আপনার কণ্ঠস্বর বিশ্লেষণ করা হচ্ছে...',
    youSaid: 'আপনি বলেছেন:',
    youEntered: 'আপনি লিখেছেন:',
    typePlaceholder: 'অথবা আপনার উত্তর এখানে টাইপ করুন...',
    startVoiceBtn: 'কথা বলুন',
    switchToTypeBtn: 'টাইপ করুন',
    mockTranscript: 'আমার তিন দিন ধরে পেটে ব্যথা হচ্ছে।',
  },

  page6_history: {
    subtitle: 'আপনি মুখে বলতে পারেন বা বিকল্প বেছে নিতে পারেন।',
    dualInputHint: 'কথা বলে জানান বা নিচের বিকল্পগুলি থেকে বেছে নিন:',
    orTapBelow: 'অথবা নিচের বিকল্পগুলি থেকে একটি বেছে নিন:',
    skipNotSure: 'এড়িয়ে যান / নিশ্চিত নন',
    listening: 'আমি শুনছি...',
    processing: 'উত্তর বিশ্লেষণ করা হচ্ছে...',
    youSaid: 'আপনি বলেছেন:',
    youEntered: 'আপনি লিখেছেন:',
    typePlaceholder: 'কাস্টম উত্তর লিখুন...',
    startVoiceBtn: 'কথা বলুন',
    switchToTypeBtn: 'টাইপ করুন',
    instruction: 'অনুগ্রহ করে কথা বলে অথবা স্ক্রিনে দেওয়া বিকল্পে স্পর্শ করে উত্তর দিন।',
    questions: {
      onset: {
        title: 'ব্যথা কবে শুরু হয়েছিল?',
        subtitle: 'আপনি মুখে বলতে পারেন বা বিকল্প বেছে নিতে পারেন।',
        options: {
          today: 'আজ',
          yesterday: 'গতকাল',
          fewDays: 'কয়েক দিন আগে',
          moreWeek: 'এক সপ্তাহেরও বেশি আগে',
        },
        mockAnswer: '৩ দিন আগে শুরু হয়েছিল',
      },
      location: {
        title: 'ঠিক কোথায় ব্যথা হচ্ছে?',
        subtitle: 'অস্বস্তির স্থানটি নির্দেশ করুন।',
        options: {
          upperAb: 'পেটের ওপরের অংশে',
          lowerAb: 'পেটের নিচের অংশে',
          chest: 'বুকে',
          allOver: 'পুরো পেটে',
        },
        mockAnswer: 'পেটের নিচের অংশে',
      },
      severity: {
        title: 'ব্যথা কতটা তীব্র?',
        subtitle: 'ব্যথার মাত্রা নির্বাচন করুন।',
        options: {
          mild: 'হালকা (সহ্য করা যায়)',
          moderate: 'মাঝারি (অস্বস্তিকর)',
          severe: 'তীব্র (সহ্য করা কঠিন)',
          verySevere: 'অত্যধিক তীব্র',
        },
        mockAnswer: 'মাঝারি তীব্রতা',
      },
      associated: {
        title: 'অন্য কোনো উপসর্গ আছে কি?',
        subtitle: 'অন্য কোনো সমস্যা থাকলে বেছে নিন।',
        options: {
          nausea: 'বমি বমি ভাব / বমি',
          fever: 'জ্বর / কাঁপুনি',
          lossAppetite: 'ক্ষুধামন্দা',
          none: 'এগুলির কোনোটিই নয়',
        },
        mockAnswer: 'বমি নেই, সামান্য ক্ষুধামন্দা রয়েছে',
      },
    },
  },

  page7_documents: {
    title: 'আপনার কাছে কি কোনো মেডিকেল নথি আছে?',
    subtitle: 'প্রেসক্রিপশন, ল্যাব রিপোর্ট, এক্স-রে বা ডিসচার্জ সামারি আপলোড করতে পারেন।',
    cardTitle: 'নথি স্ক্যান বা আপলোড করুন',
    cardSubtitle: 'নথি আপলোড করার পদ্ধতি নির্বাচন করুন',
    supportedFormats: 'সমর্থিত ফরম্যাট: PDF, JPG, PNG',
    useScanner: 'স্ক্যানার ব্যবহার করুন',
    uploadPC: 'কম্পিউটার থেকে আপলোড',
    uploadUSB: 'ইউএসবি (USB) থেকে নিন',
    scanningNotice: 'কিয়স্ক স্ক্যানার থেকে স্ক্যান করা হচ্ছে...',
    usbNotice: 'ইউএসবি ড্রাইভ পড়া হচ্ছে...',
    uploadedTitle: 'আপলোড করা নথিপত্র',
    instruction:
      'আপনার কাছে কোনো মেডিকেল নথি থাকলে কম্পিউটার বা স্ক্যানার ব্যবহার করুন, অথবা পরবর্তী বোতাম টিপুন।',
  },

  page8_review: {
    title: 'আমরা যা বুঝলাম',
    subtitle: 'অনুগ্রহ করে বিবরণটি পর্যালোচনা করুন এবং নিশ্চিত করুন।',
    sectionPatientInfo: 'আপনার তথ্য',
    sectionKeyPoints: 'কথোপকথনের মূল তথ্য',
    sectionDocs: 'সংযুক্ত নথিপত্র',
    fieldName: 'নাম',
    fieldAgeGender: 'বয়স / লিঙ্গ',
    fieldVisitType: 'ভিজিটের ধরন',
    fieldComplaint: 'মূল সমস্যা',
    visitTypeNew: 'নতুন সমস্যা',
    visitTypeFollowUp: 'ফলো-আপ ভিজিট',
    editChiefComplaintNotice:
      'মূল সমস্যা পরিবর্তন করলে প্রশ্নগুলি পুনরায় শুরু হবে।',
    editKeyPointsTitle: 'আলোচনার তথ্য সংশোধন করুন',
    voiceOption: 'কথা বলে পরিবর্তন',
    typeOption: 'টাইপ করে পরিবর্তন',
    disclaimer:
      'বিজ্ঞপ্তি: এই সংক্ষিপ্ত বিবরণটি আপনার ডাক্তারের পর্যালোচনার জন্য একটি খসড়া। এটি কোনো চূড়ান্ত রোগ নির্ণয় নয়।',
    instruction:
      'এটি আপনার সাক্ষাতের বিবরণ। অনুগ্রহ করে যাচাই করুন। পরিবর্তন করতে পারেন, অথবা পরবর্তী বোতাম টিপুন।',
    editChiefComplaintModalTitle: 'মূল সমস্যা পরিবর্তন করবেন?',
    editChiefComplaintModalContinue: 'চালিয়ে যান',
    editChooseMethodPrompt: 'আপনি কিভাবে এই উত্তরটি পরিবর্তন করতে চান?',
    editChooseAnotherMethod: 'অন্য পদ্ধতি বেছে নিন',
    noDocsAttached: 'এই সাক্ষাতের জন্য কোনো নথি সংযুক্ত করা হয়নি।',
    docPreviewLabel: 'মক নথি পূর্বদর্শন • মেডিকিয়স্ক দ্বারা যাচাইকৃত',
    docPreviewCloseBtn: 'পূর্বদর্শন বন্ধ করুন',
    docViewBtn: 'দেখুন',
    sectionPreviousVisit: 'পূর্ববর্তী ভিজিটের বিবরণ',
    fieldPreviousVisitDate: 'ভিজিটের তারিখ',
    fieldPreviousVisitDept: 'বিভাগ',
    fieldPreviousVisitComplaint: 'মূল সমস্যা',
    fieldPreviousVisitDoctor: 'পরামর্শক চিকিৎসক',
  },

  page9_confirmation: {
    title: 'ধন্যবাদ!',
    subtitle: 'আপনার তথ্য সফলভাবে নথিভুক্ত করা হয়েছে।',
    nextStepsTitle: 'এরপর কি হবে?',
    step1: 'ডাক্তার আপনার তথ্য ও নথিপত্র পর্যালোচনা করবেন।',
    step2: 'আপনার পালা এলে ওপিডি স্ক্রিনে আপনার নাম ও টোকেন ডাকা হবে।',
    step3: 'আপনি অপেক্ষা কক্ষে আরাম করে বসতে পারেন।',
    tokenLabel: 'আপনার টোকেন নম্বর',
    autoReturnMessage: '{seconds} সেকেন্ডে মূল পর্দায় ফিরে যাওয়া হচ্ছে',
    instruction:
      'ধন্যবাদ! আপনার তথ্য নথিভুক্ত হয়েছে। অনুগ্রহ করে টোকেন ডাকা পর্যন্ত অপেক্ষা করুন।',
  },

  page10_followUp: {
    title: 'আপনার পূর্ববর্তী ভিজিট নির্বাচন করুন',
    subtitle: 'যে তারিখে নতুন রিপোর্ট যুক্ত করতে চান সেটি বেছে নিন।',
    consultingDoctor: 'পরামর্শক চিকিৎসক',
    instruction:
      'আপনার পূর্ববর্তী ভিজিট নির্বাচন করুন, তারপর পরবর্তী বোতাম টিপুন।',
  },
}
