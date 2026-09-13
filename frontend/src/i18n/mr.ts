import type { TranslationSchema } from './types'

export const mr: TranslationSchema = {
  common: {
    next: 'पुढे जा',
    back: 'मागे या',
    edit: 'बदला',
    skip: 'वगळा / खात्री नाही',
    confirm: 'निश्चित करा',
    retry: 'पुन्हा बोला',
    submit: 'जतन करा',
    cancel: 'रद्द करा',
    hearAgain: 'पुन्हा ऐका',
    mute: 'आवाज बंद (Mute)',
    unmute: 'आवाज सुरू करा',
    backToHome: 'मुख्य पृष्ठावर जा',
    save: 'जतन करा',
    done: 'पूर्ण',
    ready: 'तयार',
    verified: 'सत्यापित',
  },

  header: {
    brandName: 'MediKiosk (मेडीकियोस्क)',
    tagline: 'तुमचे आरोग्य, आमचे प्राधान्य.',
  },

  page1_language: {
    title: 'मेडीकियोस्क मध्ये आपले स्वागत आहे',
    subtitle: 'आपली पसंतीची भाषा निवडा',
    instruction: 'मेडीकियोस्क मध्ये आपले स्वागत आहे. कृपया आपली पसंतीची भाषा निवडा.',
  },

  page2_consent: {
    title: 'तुमची गोपनीयता महत्त्वाची आहे',
    subtitle: 'पुढे जाण्यासाठी आम्हाला तुमची परवानगी हवी आहे. आम्ही गोळा करू शकतो:',
    itemAnswers: 'तुमची उत्तरे (बोलून किंवा लिहून)',
    itemDocs: 'तुमची जुनी वैद्यकीय कागदपत्रे',
    itemHistory: 'तुमचा पूर्वीचा वैद्यकीय इतिहास',
    btnAgree: 'मी सहमत आहे',
    btnDecline: 'मी सहमत नाही',
    instruction:
      'तुमची गोपनीयता महत्त्वाची आहे. डॉक्टरांसोबत माहिती सामायिक करण्यास सहमत असल्यास हिरवे बटण दाबा. सहमत नसल्यास लाल बटण दाबा.',
    modalTitle: 'संमती आवश्यक आहे',
    modalDesc:
      'डॉक्टरांसाठी माहिती तयार करण्यासाठी मेडीकियोस्कला आपली परवानगी आवश्यक आहे. तुमचा डेटा सुरक्षित राहतो आणि भेटीनंतर काढला जातो.',
    modalBtnAgree: 'मला समजले, मी सहमत आहे',
    modalBtnReturn: 'भाषा निवडीवर परत जा',
  },

  page3_identification: {
    title: 'तुमची ओळख निश्चित करा',
    subtitle: 'पुढे जाण्यासाठी एक पर्याय निवडा',
    aadhaarTitle: 'आधार कार्ड',
    aadhaarDesc: 'ओळखीसाठी आधार कार्ड वापरा',
    abhaTitle: 'आभा आयडी (ABHA ID)',
    abhaDesc: 'तुमचा आयुष्मान भारत आरोग्य आयडी वापरा',
    manualTitle: 'स्वतः माहिती भरा',
    manualDesc: 'तुमचे नाव आणि फोन नंबर प्रविष्ट करा',
    instruction:
      'तुमची ओळख निश्चित करा. आधार, आभा आयडी किंवा स्वतः माहिती भरण्याचा पर्याय निवडा.',
    modalTitleAadhaar: 'आधार पडताळणी',
    modalTitleAbha: 'आभा आयडी पडताळणी',
    modalTitleManual: 'रुग्ण माहिती',
    modalDemoNotice: 'डेमो सिम्युलेशन: कोणताही खरा आधार किंवा आभा डेटा साठवला जात नाही.',
    modalProfileTitle: 'पडताळलेली रुग्ण माहिती',
    modalBtnConfirm: 'निश्चित करून पुढे जा',
  },

  page4_visitReason: {
    title: 'आज येण्याचे कारण काय आहे?',
    subtitle: 'योग्य पर्याय निवडा',
    newProblemTitle: 'मला आरोग्याची समस्या आहे',
    newProblemDesc: 'तुमची लक्षणे किंवा त्रासाबद्दल सांगा',
    followUpTitle: 'फॉलो-अप (पुनर्भेट)',
    followUpDesc: 'माझ्याकडे नवीन अहवाल किंवा कागदपत्रे जोडायची आहेत',
    instruction:
      'आज येण्याचे कारण काय आहे? नवीन त्रासासाठी आरोग्याची समस्या निवडा, किंवा जुन्या तपासणीसाठी फॉलो-अप निवडा.',
  },

  page5_complaint: {
    title: 'तुमच्या त्रासाबद्दल सांगा',
    subtitle: 'तुम्ही साध्या भाषेत बोलू शकता. वैद्यकीय शब्दांची गरज नाही.',
    instruction:
      'तुमच्या त्रासाबद्दल सांगा. तुम्ही साध्या भाषेत बोलू शकता. वैद्यकीय शब्दांची गरज नाही.',
    listening: 'मी ऐकत आहे...',
    processing: 'तुमचा आवाज तपासत आहे...',
    youSaid: 'तुम्ही म्हणालात:',
    youEntered: 'तुम्ही लिहिले:',
    typePlaceholder: 'किंवा तुमचे उत्तर येथे टाइप करा...',
    startVoiceBtn: 'बोलून सांगा',
    switchToTypeBtn: 'टाइप करून सांगा',
    mockTranscript: 'मला तीन दिवसांपासून पोटात दुखत आहे.',
  },

  page6_history: {
    subtitle: 'तुम्ही बोलू शकता किंवा पर्यायावर स्पर्श करू शकता.',
    dualInputHint: 'बोलून सांगा किंवा खालीलपैकी एक पर्याय निवडा:',
    orTapBelow: 'किंवा खालील पर्याय निवडा:',
    skipNotSure: 'वगळा / खात्री नाही',
    listening: 'मी ऐकत आहे...',
    processing: 'उत्तर तपासत आहे...',
    youSaid: 'तुम्ही म्हणालात:',
    youEntered: 'तुम्ही लिहिले:',
    typePlaceholder: 'उत्तर येथे टाइप करा...',
    startVoiceBtn: 'बोलून सांगा',
    switchToTypeBtn: 'टाइप करून सांगा',
    instruction: 'कृपया बोलून किंवा स्क्रीनवरील पर्यायावर स्पर्श करून उत्तर द्या.',
    questions: {
      onset: {
        title: 'त्रास कधी सुरू झाला?',
        subtitle: 'तुम्ही बोलू शकता किंवा पर्याय निवडू शकता.',
        options: {
          today: 'आज',
          yesterday: 'काल',
          fewDays: 'काही दिवसांपूर्वी',
          moreWeek: 'एका आठवड्यापेक्षा जास्त वेळ',
        },
        mockAnswer: '३ दिवसांपूर्वी सुरू झाला',
      },
      location: {
        title: 'नक्की कुठे दुखत आहे?',
        subtitle: 'दुखत असलेली जागा निवडा.',
        options: {
          upperAb: 'पोटाच्या वरच्या भागात',
          lowerAb: 'पोटाच्या खालच्या भागात',
          chest: 'छातीत',
          allOver: 'संपूर्ण पोटात',
        },
        mockAnswer: 'पोटाच्या खालच्या भागात',
      },
      severity: {
        title: 'त्रास किती तीव्र आहे?',
        subtitle: 'दुखण्याची तीव्रता निवडा.',
        options: {
          mild: 'कमी (सहन होण्यासारखा)',
          moderate: 'मध्यम (त्रासदायक)',
          severe: 'जास्त (सहन न होणारा)',
          verySevere: 'खूप जास्त तीव्र',
        },
        mockAnswer: 'मध्यम तीव्रतेचा त्रास',
      },
      associated: {
        title: 'इतर काही लक्षणे आहेत का?',
        subtitle: 'इतर त्रास होत असल्यास निवडा.',
        options: {
          nausea: 'मळमळ / उलटी',
          fever: 'ताप / थंडी वाजणे',
          lossAppetite: 'भूक न लागणे',
          none: 'यापैकी काहीही नाही',
        },
        mockAnswer: 'उलटी नाही, थोडी भूक मंदावली आहे',
      },
    },
  },

  page7_documents: {
    title: 'काही वैद्यकीय कागदपत्रे जोडायची आहेत का?',
    subtitle: 'तुम्ही प्रिस्क्रिप्शन, लॅब रिपोर्ट, एक्स-रे किंवा डिस्चार्ज कार्ड अपलोड करू शकता.',
    cardTitle: 'कागदपत्रे स्कॅन किंवा अपलोड करा',
    cardSubtitle: 'कागदपत्रे जोडण्यासाठी योग्य पर्याय निवडा',
    supportedFormats: 'समर्थित फॉरमॅट: PDF, JPG, PNG',
    useScanner: 'स्कॅनर वापरा',
    uploadPC: 'संगणकावरून अपलोड करा',
    uploadUSB: 'यूएसबी (USB) वरून जोडा',
    scanningNotice: 'कियोस्क स्कॅनरवरून स्कॅनिंग सुरू आहे...',
    usbNotice: 'यूएसबी ड्राईव्ह तपासत आहे...',
    uploadedTitle: 'अपलोड केलेली कागदपत्रे',
    instruction:
      'काही कागदपत्रे जोडायची असल्यास संगणक किंवा स्कॅनर वापरा, किंवा पुढे जा दाबा.',
  },

  page8_review: {
    title: 'आम्ही समजलेली माहिती',
    subtitle: 'कृपया माहिती तपासा आणि पुष्टी करा.',
    sectionPatientInfo: 'तुमची माहिती',
    sectionKeyPoints: 'संभाषणातील मुख्य मुद्दे',
    sectionDocs: 'जोडलेली कागदपत्रे',
    fieldName: 'नाव',
    fieldAgeGender: 'वय / लिंग',
    fieldVisitType: 'भेटीचा प्रकार',
    fieldComplaint: 'मुख्य त्रास',
    visitTypeNew: 'नवीन समस्या',
    visitTypeFollowUp: 'फॉलो-अप भेट',
    editChiefComplaintNotice:
      'मुख्य त्रासात बदल केल्यास सविस्तर प्रश्न पुन्हा सुरू होतील.',
    editKeyPointsTitle: 'संभाषणातील मुद्दा बदला',
    voiceOption: 'बोलून बदला',
    typeOption: 'टाइप करून बदला',
    disclaimer:
      'सूचना: हा सारांश डॉक्टरांच्या पुनरावलोकनासाठी तयार केलेला कच्चा मसुदा आहे. हा अंतिम वैद्यकीय निष्कर्ष नाही.',
    instruction:
      'ही तुमच्या भेटीची नोंद आहे. कृपया तपासा. बदल करायचा असल्यास बदल करू शकता, किंवा पुढे जा दाबा.',
    editChiefComplaintModalTitle: 'मुख्य त्रास बदलायचा का?',
    editChiefComplaintModalContinue: 'पुढे चालू ठेवा',
    editChooseMethodPrompt: 'हे उत्तर कसे बदलायचे आहे?',
    editChooseAnotherMethod: 'दुसरा पर्याय निवडा',
    noDocsAttached: 'या भेटीसाठी कोणतीही कागदपत्रे जोडलेली नाहीत.',
    docPreviewLabel: 'मॉक कागदपत्र पूर्वावलोकन • मेडीकियोस्क द्वारे सत्यापित',
    docPreviewCloseBtn: 'पूर्वावलोकन बंद करा',
    docViewBtn: 'पहा',
    sectionPreviousVisit: 'मागील भेटीचा तपशील',
    fieldPreviousVisitDate: 'भेटीची तारीख',
    fieldPreviousVisitDept: 'विभाग',
    fieldPreviousVisitComplaint: 'मूळ त्रास',
    fieldPreviousVisitDoctor: 'सल्लागार डॉक्टर',
  },

  page9_confirmation: {
    title: 'धन्यवाद!',
    subtitle: 'तुमची माहिती यशस्वीरीत्या नोंदवली गेली आहे.',
    nextStepsTitle: 'पुढे काय होईल?',
    step1: 'डॉक्टर तुमची माहिती आणि कागदपत्रे तपासतील.',
    step2: 'तुमचा नंबर आल्यावर ओपीडी स्क्रीनवर नाव पुकारले जाईल.',
    step3: 'तुम्ही प्रतीक्षा कक्षात शांतपणे बसू शकता.',
    tokenLabel: 'तुमचा टोकन क्रमांक',
    autoReturnMessage: '{seconds} सेकंदात मुख्य पृष्ठावर जात आहे',
    instruction:
      'धन्यवाद! तुमची माहिती नोंदवली गेली आहे. कृपया तुमचा नंबर येईपर्यंत प्रतीक्षा कक्षात बसा.',
  },

  page10_followUp: {
    title: 'तुमची मागील भेट निवडा',
    subtitle: 'ज्या भेटीशी नवीन अहवाल जोडायचे आहेत ती भेट निवडा.',
    consultingDoctor: 'सल्लागार डॉक्टर',
    instruction:
      'तुमची मागील भेट निवडा, आणि पुढे जा दाबा.',
  },
}
