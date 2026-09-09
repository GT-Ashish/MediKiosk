import React, { useState, useRef, useEffect } from 'react'
import { useKiosk } from '../../context/KioskContext'
import { useInstructionPlayer } from '../../hooks/useInstructionPlayer'
import { HearAgainButton } from '../../components/patient/HearAgainButton'
import {
  startSpeechRecognition,
  stopSpeaking,
  type SpeechRecognitionControls,
} from '../../utils/speech'

type KeyPointKey = 'onset' | 'location' | 'severity' | 'associated'

export const ReviewSummaryPage: React.FC = () => {
  const {
    patient,
    visitType,
    chiefComplaint,
    historyAnswers,
    updateHistoryAnswer,
    editChiefComplaintFlow,
    documents,
    goTo,
    goBack,
    t,
    isMuted,
    selectedLanguage,
  } = useKiosk()

  const isNewProblem = visitType === 'new_problem'

  // Chief Complaint Confirmation Modal
  const [showChiefComplaintConfirm, setShowChiefComplaintConfirm] = useState(false)

  // Key Point Editing State
  const [editingKey, setEditingKey] = useState<KeyPointKey | null>(null)
  const [editMode, setEditMode] = useState<'choose' | 'voice' | 'type'>('choose')
  const [isVoiceListening, setIsVoiceListening] = useState(false)
  const [isVoiceProcessing, setIsVoiceProcessing] = useState(false)
  const [voiceDraft, setVoiceDraft] = useState('')
  const [typedDraft, setTypedDraft] = useState('')
  const voiceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const recognitionControlsRef = useRef<SpeechRecognitionControls | null>(null)

  // Document preview modal
  const [viewingDoc, setViewingDoc] = useState<string | null>(null)

  const {
    status,
    currentRepetition,
    totalRepetitions,
    isPlaying,
    replay,
  } = useInstructionPlayer({
    instruction: t.page8_review.instruction,
    repeatCount: 2,
    autoPlay: true,
    langCode: selectedLanguage.code,
    isMuted,
  })

  // Dynamic summary key points derived from history answers
  const keyPointsList: { key: KeyPointKey; label: string; value: string }[] = [
    {
      key: 'onset',
      label: t.page6_history.questions.onset.title,
      value: historyAnswers.onset || t.page6_history.questions.onset.mockAnswer,
    },
    {
      key: 'location',
      label: t.page6_history.questions.location.title,
      value: historyAnswers.location || t.page6_history.questions.location.mockAnswer,
    },
    {
      key: 'severity',
      label: t.page6_history.questions.severity.title,
      value: historyAnswers.severity || t.page6_history.questions.severity.mockAnswer,
    },
    {
      key: 'associated',
      label: t.page6_history.questions.associated.title,
      value: historyAnswers.associated || t.page6_history.questions.associated.mockAnswer,
    },
  ]

  // Item 12: Edit Chief Complaint triggers flow back to Page 5 & resets history
  const handleStartChiefComplaintEdit = () => {
    setShowChiefComplaintConfirm(true)
  }

  const handleConfirmChiefComplaintEdit = () => {
    setShowChiefComplaintConfirm(false)
    editChiefComplaintFlow()
  }

  const abortVoiceEditRecognition = () => {
    if (recognitionControlsRef.current) {
      try {
        recognitionControlsRef.current.abort()
      } catch {
        // ignore
      }
      recognitionControlsRef.current = null
    }
  }

  // Clean up timers & speech on unmount
  useEffect(() => {
    return () => {
      if (voiceTimerRef.current) clearTimeout(voiceTimerRef.current)
      abortVoiceEditRecognition()
      stopSpeaking()
    }
  }, [])

  // Item 13: Edit Key Points (Voice + Type dual options)
  const handleOpenEditKeyPoint = (key: KeyPointKey, currentValue: string) => {
    abortVoiceEditRecognition()
    if (voiceTimerRef.current) clearTimeout(voiceTimerRef.current)
    setEditingKey(key)
    setEditMode('choose')
    setTypedDraft(currentValue)
    setVoiceDraft('')
    setIsVoiceListening(false)
    setIsVoiceProcessing(false)
  }

  const handleStartVoiceEdit = () => {
    stopSpeaking()
    abortVoiceEditRecognition()
    if (voiceTimerRef.current) clearTimeout(voiceTimerRef.current)

    setEditMode('voice')
    setIsVoiceListening(true)
    setIsVoiceProcessing(false)
    setVoiceDraft('')

    let hasReceivedFinal = false

    // Fallback timer (3.5s)
    voiceTimerRef.current = setTimeout(() => {
      if (hasReceivedFinal) return
      abortVoiceEditRecognition()
      setIsVoiceListening(false)
      setIsVoiceProcessing(true)

      voiceTimerRef.current = setTimeout(() => {
        setIsVoiceProcessing(false)
        if (editingKey) {
          const mockResult = `${t.page6_history.questions[editingKey].mockAnswer} (Updated)`
          setVoiceDraft(mockResult)
        }
      }, 800)
    }, 3500)

    // Start real browser SpeechRecognition
    const controls = startSpeechRecognition(selectedLanguage.code, {
      onResult: (transcriptText, isFinal) => {
        setVoiceDraft(transcriptText)

        if (isFinal && transcriptText.trim()) {
          hasReceivedFinal = true
          if (voiceTimerRef.current) clearTimeout(voiceTimerRef.current)
          abortVoiceEditRecognition()
          setIsVoiceListening(false)
          setIsVoiceProcessing(true)

          voiceTimerRef.current = setTimeout(() => {
            setIsVoiceProcessing(false)
            setVoiceDraft(transcriptText.trim())
          }, 700)
        }
      },
      onEnd: (finalTranscript) => {
        if (hasReceivedFinal) return
        if (finalTranscript.trim()) {
          hasReceivedFinal = true
          if (voiceTimerRef.current) clearTimeout(voiceTimerRef.current)
          setIsVoiceListening(false)
          setIsVoiceProcessing(true)

          voiceTimerRef.current = setTimeout(() => {
            setIsVoiceProcessing(false)
            setVoiceDraft(finalTranscript.trim())
          }, 700)
        }
      },
      onError: (err) => {
        console.warn('[Review Key-Point Voice Edit Notice]:', err?.error || err)
      },
    })

    recognitionControlsRef.current = controls
  }

  const handleSaveVoiceEdit = () => {
    abortVoiceEditRecognition()
    if (voiceTimerRef.current) clearTimeout(voiceTimerRef.current)
    if (editingKey && voiceDraft.trim()) {
      updateHistoryAnswer(editingKey, voiceDraft.trim())
      setEditingKey(null)
    }
  }

  const handleStartTypeEdit = () => {
    abortVoiceEditRecognition()
    if (voiceTimerRef.current) clearTimeout(voiceTimerRef.current)
    setEditMode('type')
    setIsVoiceListening(false)
    setIsVoiceProcessing(false)
  }

  const handleSaveTypeEdit = (e: React.FormEvent) => {
    e.preventDefault()
    abortVoiceEditRecognition()
    if (voiceTimerRef.current) clearTimeout(voiceTimerRef.current)
    if (editingKey && typedDraft.trim()) {
      updateHistoryAnswer(editingKey, typedDraft.trim())
      setEditingKey(null)
    }
  }

  return (
    <div className="flex flex-col items-center justify-between min-h-[calc(100vh-140px)] max-w-4xl w-full mx-auto px-6 py-6 select-none">
      {/* Heading - Desktop First */}
      <div className="text-center my-2 max-w-2xl">
        <h2 className="text-3xl sm:text-4xl font-bold text-[#243331] mb-2 tracking-tight">
          {t.page8_review.title}
        </h2>
        <p className="text-base sm:text-lg text-[#647471] font-medium">
          {t.page8_review.subtitle}
        </p>
      </div>

      {/* Main Review Summary Card (Desktop-First Wide Card) */}
      <div className="w-full bg-[#FFFFFF] border border-[#D9E2DF] rounded-3xl p-6 sm:p-8 shadow-sm my-4 space-y-6">
        {/* Section 1: Your Information */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-bold text-[#243331] flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-[#2F7D73]" />
              {t.page8_review.sectionPatientInfo}
            </h3>
            {/* Item 10 & 11: Only show Edit if New Problem */}
            {isNewProblem && (
              <button
                type="button"
                onClick={handleStartChiefComplaintEdit}
                className="text-xs font-semibold text-[#2F7D73] hover:text-[#276B63] bg-[#DCEDEA] hover:bg-[#CFE5E1] px-3 py-1.5 rounded-lg flex items-center gap-1.5 cursor-pointer transition-colors"
                title="Edit chief complaint"
              >
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                </svg>
                <span>{t.common.edit}</span>
              </button>
            )}
          </div>

          <dl className="grid grid-cols-1 sm:grid-cols-2 gap-y-3 gap-x-6 text-sm sm:text-base bg-[#F6F8F7] p-4 sm:p-5 rounded-2xl border border-[#EBF0EE]">
            <div>
              <dt className="text-xs uppercase font-bold text-[#647471] tracking-wider mb-0.5">{t.page8_review.fieldName}</dt>
              <dd className="font-bold text-[#243331] text-lg">{patient.name}</dd>
            </div>

            <div>
              <dt className="text-xs uppercase font-bold text-[#647471] tracking-wider mb-0.5">{t.page8_review.fieldAgeGender}</dt>
              <dd className="font-semibold text-[#243331] text-lg">{patient.age} years / {patient.gender}</dd>
            </div>

            <div>
              <dt className="text-xs uppercase font-bold text-[#647471] tracking-wider mb-0.5">{t.page8_review.fieldVisitType}</dt>
              <dd className="font-semibold text-[#2F7D73] text-lg">
                {visitType === 'new_problem' ? t.page8_review.visitTypeNew : t.page8_review.visitTypeFollowUp}
              </dd>
            </div>

            <div>
              <dt className="text-xs uppercase font-bold text-[#647471] tracking-wider mb-0.5">{t.page8_review.fieldComplaint}</dt>
              <dd className="font-bold text-[#243331] text-lg">{chiefComplaint}</dd>
            </div>
          </dl>
        </div>

        {/* Section 2: Key Points from Conversation */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-bold text-[#243331] flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-[#2F7D73]" />
              {t.page8_review.sectionKeyPoints}
            </h3>
          </div>

          <div className="space-y-2.5 bg-[#F6F8F7] p-4 sm:p-5 rounded-2xl border border-[#EBF0EE]">
            {keyPointsList.map((pt) => (
              <div
                key={pt.key}
                className="flex items-center justify-between p-3.5 bg-white rounded-2xl border border-[#EBF0EE] shadow-2xs gap-3"
              >
                <div className="flex items-start gap-2.5 flex-1">
                  <span className="text-[#2F7D73] font-bold text-lg leading-none mt-0.5">•</span>
                  <div>
                    <span className="text-xs font-bold uppercase tracking-wider text-[#647471] block">
                      {pt.label}
                    </span>
                    <span className="text-base font-semibold text-[#243331]">
                      {pt.value}
                    </span>
                  </div>
                </div>

                {/* Item 10 & 13: Only show Edit if New Problem */}
                {isNewProblem && (
                  <button
                    type="button"
                    onClick={() => handleOpenEditKeyPoint(pt.key, pt.value)}
                    className="text-xs font-semibold text-[#2F7D73] hover:text-[#276B63] bg-[#DCEDEA] hover:bg-[#CFE5E1] px-3 py-1.5 rounded-lg flex items-center gap-1.5 cursor-pointer transition-colors flex-shrink-0"
                  >
                    <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
                    </svg>
                    <span>{t.common.edit}</span>
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Section 3: Uploaded Documents */}
        <div>
          <h3 className="text-lg font-bold text-[#243331] mb-3 flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-[#2F7D73]" />
            {t.page8_review.sectionDocs} ({documents.length})
          </h3>
          {documents.length > 0 ? (
            <div className="space-y-2">
              {documents.map((doc) => (
                <div
                  key={doc.id}
                  className="flex items-center justify-between p-3.5 bg-[#F6F8F7] rounded-xl border border-[#EBF0EE]"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-lg bg-[#DCEDEA] text-[#2F7D73] flex items-center justify-center">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <span className="text-sm font-semibold text-[#243331]">{doc.title}</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => setViewingDoc(doc.title)}
                    className="text-xs font-semibold text-[#2563EB] hover:underline cursor-pointer"
                  >
                    👁 View
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-[#647471] italic">No prior documents attached for this visit.</p>
          )}
        </div>

        {/* Clinical Safety Draft Disclaimer */}
        <div className="p-4 bg-[#EFF6FF] border border-[#BFDBFE] rounded-2xl text-xs text-[#1D4ED8]">
          <span className="font-bold">Notice:</span> {t.page8_review.disclaimer}
        </div>
      </div>

      {/* Bottom Bar: Back + Hear Again + Next (Item 14: Next, not Looks Correct) */}
      <div className="w-full flex items-center justify-between mt-auto pt-4 border-t border-[#D9E2DF]">
        <button
          type="button"
          onClick={goBack}
          className="px-6 py-3.5 rounded-xl border border-[#D9E2DF] bg-white hover:bg-gray-50 text-base font-semibold text-[#243331] flex items-center gap-2 transition-colors cursor-pointer shadow-xs min-h-[48px]"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M15 19l-7-7 7-7" />
          </svg>
          <span>{t.common.back}</span>
        </button>

        <HearAgainButton
          onHearAgain={replay}
          status={status}
          currentRepetition={currentRepetition}
          totalRepetitions={totalRepetitions}
          isPlaying={isPlaying}
        />

        <button
          type="button"
          onClick={() => goTo('confirmation')}
          className="px-8 py-3.5 bg-[#4F8A6D] hover:bg-[#3E6E56] active:bg-[#335B47] text-white font-bold text-base rounded-xl shadow-md flex items-center gap-2 transition-all cursor-pointer min-h-[48px]"
        >
          <span>{t.common.next}</span>
          <svg className="w-5 h-5 stroke-current stroke-2" fill="none" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
          </svg>
        </button>
      </div>

      {/* Item 12: Chief Complaint Edit Warning / Redirect Modal */}
      {showChiefComplaintConfirm && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-3xl p-6 sm:p-8 max-w-md w-full shadow-2xl border border-[#D9E2DF]">
            <div className="w-12 h-12 rounded-full bg-[#EFF6FF] text-[#2563EB] flex items-center justify-center mb-3">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-[#243331] mb-2">
              Edit Chief Complaint?
            </h3>
            <p className="text-sm text-[#647471] mb-6">
              {t.page8_review.editChiefComplaintNotice}
            </p>
            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => setShowChiefComplaintConfirm(false)}
                className="flex-1 py-3 border border-[#D9E2DF] text-[#647471] font-semibold rounded-xl text-base hover:bg-gray-50 cursor-pointer"
              >
                {t.common.cancel}
              </button>
              <button
                type="button"
                onClick={handleConfirmChiefComplaintEdit}
                className="flex-1 py-3 bg-[#2F7D73] text-white font-bold rounded-xl text-base hover:bg-[#276B63] shadow-md cursor-pointer"
              >
                Continue
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Item 13: Edit Key Points Modal with BOTH [ 🎤 Voice ] and [ ⌨ Type ] */}
      {editingKey && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-3xl p-6 sm:p-8 max-w-lg w-full shadow-2xl border border-[#D9E2DF]">
            <h3 className="text-xl font-bold text-[#243331] mb-1">
              {t.page8_review.editKeyPointsTitle}
            </h3>
            <p className="text-xs uppercase font-bold text-[#2F7D73] tracking-wider mb-4">
              {keyPointsList.find((k) => k.key === editingKey)?.label}
            </p>

            {/* Mode 1: Choose between Voice or Type */}
            {editMode === 'choose' && (
              <div className="space-y-4">
                <p className="text-sm text-[#647471]">
                  How would you like to update this answer?
                </p>
                <div className="grid grid-cols-2 gap-4">
                  {/* Voice Button */}
                  <button
                    type="button"
                    onClick={handleStartVoiceEdit}
                    className="p-5 rounded-2xl bg-[#E8F4F1] border-2 border-[#2F7D73] hover:bg-[#DCEDEA] text-[#2F7D73] flex flex-col items-center justify-center gap-2 cursor-pointer font-bold transition-all shadow-xs"
                  >
                    <div className="w-12 h-12 rounded-full bg-[#2F7D73] text-white flex items-center justify-center shadow-sm">
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                      </svg>
                    </div>
                    <span>🎤 {t.page8_review.voiceOption}</span>
                  </button>

                  {/* Type Button */}
                  <button
                    type="button"
                    onClick={handleStartTypeEdit}
                    className="p-5 rounded-2xl bg-[#F6F8F7] border-2 border-[#D9E2DF] hover:border-[#2F7D73] hover:bg-white text-[#243331] flex flex-col items-center justify-center gap-2 cursor-pointer font-bold transition-all shadow-xs"
                  >
                    <div className="w-12 h-12 rounded-full bg-[#647471] text-white flex items-center justify-center shadow-sm">
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <span>⌨ {t.page8_review.typeOption}</span>
                  </button>
                </div>

                <div className="pt-2 flex justify-end">
                  <button
                    type="button"
                    onClick={() => setEditingKey(null)}
                    className="px-4 py-2 border border-[#D9E2DF] text-[#647471] text-sm font-semibold rounded-xl hover:bg-gray-50 cursor-pointer"
                  >
                    {t.common.cancel}
                  </button>
                </div>
              </div>
            )}

            {/* Mode 2: Voice Interaction */}
            {editMode === 'voice' && (
              <div className="flex flex-col items-center text-center space-y-4 py-2">
                {isVoiceListening ? (
                  <div className="space-y-3">
                    <div className="w-16 h-16 rounded-full bg-[#2F7D73] text-white flex items-center justify-center mx-auto shadow-md animate-pulse">
                      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                      </svg>
                    </div>
                    <p className="text-base font-bold text-[#243331]">{t.page6_history.listening}</p>
                  </div>
                ) : isVoiceProcessing ? (
                  <div className="space-y-3">
                    <div className="w-12 h-12 border-3 border-[#2F7D73] border-t-transparent rounded-full animate-spin mx-auto" />
                    <p className="text-base font-bold text-[#243331]">{t.page6_history.processing}</p>
                  </div>
                ) : voiceDraft ? (
                  <div className="w-full space-y-4 text-left">
                    <div className="p-4 bg-[#EBF4EE] border-2 border-[#4F8A6D] rounded-2xl">
                      <span className="text-xs font-bold uppercase tracking-wider text-[#4F8A6D] block mb-1">
                        {t.page6_history.youSaid}
                      </span>
                      <p className="text-lg font-bold text-[#243331] italic">"{voiceDraft}"</p>
                    </div>
                    <div className="flex gap-2">
                      <button
                        type="button"
                        onClick={handleStartVoiceEdit}
                        className="flex-1 py-3 border border-[#D9E2DF] text-[#243331] font-semibold rounded-xl text-sm hover:bg-gray-50 cursor-pointer"
                      >
                        {t.common.retry}
                      </button>
                      <button
                        type="button"
                        onClick={handleSaveVoiceEdit}
                        className="flex-1 py-3 bg-[#4F8A6D] text-white font-bold rounded-xl text-sm hover:bg-[#3E6E56] shadow-md cursor-pointer"
                      >
                        {t.common.save}
                      </button>
                    </div>
                  </div>
                ) : null}

                <button
                  type="button"
                  onClick={() => setEditMode('choose')}
                  className="text-xs text-[#647471] hover:underline pt-2 cursor-pointer"
                >
                  Choose another method
                </button>
              </div>
            )}

            {/* Mode 3: Typing Interaction */}
            {editMode === 'type' && (
              <form onSubmit={handleSaveTypeEdit} className="space-y-4">
                <textarea
                  value={typedDraft}
                  onChange={(e) => setTypedDraft(e.target.value)}
                  className="w-full h-28 p-3.5 border-2 border-[#2F7D73] rounded-2xl text-base text-[#243331] outline-none resize-none shadow-xs"
                  autoFocus
                />
                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => setEditMode('choose')}
                    className="px-4 py-3 border border-[#D9E2DF] text-[#647471] font-semibold rounded-xl text-sm hover:bg-gray-50 cursor-pointer"
                  >
                    {t.common.cancel}
                  </button>
                  <button
                    type="button"
                    onClick={handleStartVoiceEdit}
                    className="px-4 py-3 border border-[#2F7D73] text-[#2F7D73] font-semibold rounded-xl text-sm hover:bg-[#DCEDEA] cursor-pointer"
                  >
                    🎤 {t.page8_review.voiceOption}
                  </button>
                  <button
                    type="submit"
                    disabled={!typedDraft.trim()}
                    className="flex-1 py-3 bg-[#4F8A6D] disabled:opacity-50 text-white font-bold rounded-xl text-sm hover:bg-[#3E6E56] shadow-md cursor-pointer"
                  >
                    {t.common.save}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}

      {/* Document Preview Modal */}
      {viewingDoc && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-3xl p-6 max-w-md w-full shadow-2xl border border-[#D9E2DF] text-center">
            <div className="w-12 h-12 rounded-xl bg-[#DCEDEA] text-[#2F7D73] flex items-center justify-center mx-auto mb-3">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-bold text-[#243331] mb-1">{viewingDoc}</h3>
            <p className="text-xs text-[#647471] mb-4">Mock Document Preview • Verified by MediKiosk</p>
            <div className="h-40 bg-[#F6F8F7] border border-[#D9E2DF] rounded-xl flex items-center justify-center text-xs text-[#647471] mb-4 p-4">
              [Simulated Document Content: CBC & Metabolic Profile Within Normal Limits]
            </div>
            <button
              type="button"
              onClick={() => setViewingDoc(null)}
              className="w-full py-3 bg-[#2F7D73] text-white font-bold rounded-xl text-sm cursor-pointer"
            >
              Close Preview
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
