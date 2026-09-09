import React, { useState, useRef } from 'react'
import { useKiosk } from '../../context/KioskContext'
import type { MedicalDocument } from '../../types'
import { useInstructionPlayer } from '../../hooks/useInstructionPlayer'
import { HearAgainButton } from '../../components/patient/HearAgainButton'

export const DocumentsPage: React.FC = () => {
  const { documents, addDocument, goTo, goBack, t, isMuted, selectedLanguage } = useKiosk()
  const [isScanning, setIsScanning] = useState(false)
  const [scanProgress, setScanProgress] = useState('')
  const fileInputRef = useRef<HTMLInputElement | null>(null)

  const {
    status,
    currentRepetition,
    totalRepetitions,
    isPlaying,
    replay,
  } = useInstructionPlayer({
    instruction: t.page7_documents.instruction,
    repeatCount: 2,
    autoPlay: true,
    langCode: selectedLanguage.code,
    isMuted,
  })

  // 1. Scanner Simulation
  const handleSimulateScanner = () => {
    setIsScanning(true)
    setScanProgress(t.page7_documents.scanningNotice)

    setTimeout(() => {
      setScanProgress('Scanning prescription page 1...')
      setTimeout(() => {
        const newDoc: MedicalDocument = {
          id: `doc-${Date.now()}`,
          title: `Prescription — OPD ${new Date().toLocaleDateString('en-GB')}.pdf`,
          type: 'prescription',
          date: 'Today',
          size: '1.2 MB',
          status: 'verified',
        }
        addDocument(newDoc)
        setIsScanning(false)
        setScanProgress('')
      }, 1500)
    }, 1200)
  }

  // 2. USB Simulation
  const handleSimulateUSB = () => {
    setIsScanning(true)
    setScanProgress(t.page7_documents.usbNotice)

    setTimeout(() => {
      setScanProgress('Importing X-Ray Chest PA View.jpg...')
      setTimeout(() => {
        const newDoc: MedicalDocument = {
          id: `doc-${Date.now()}`,
          title: 'X-Ray Chest PA View.jpg',
          type: 'xray',
          date: '02 Sep 2026',
          size: '3.8 MB',
          status: 'verified',
        }
        addDocument(newDoc)
        setIsScanning(false)
        setScanProgress('')
      }, 1400)
    }, 1000)
  }

  // 3. Native PC Upload via Browser File Picker (Item 9)
  const handleTriggerPCUpload = () => {
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
      fileInputRef.current.click()
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const formattedSize =
        file.size > 1024 * 1024
          ? `${(file.size / (1024 * 1024)).toFixed(1)} MB`
          : `${Math.max(1, Math.round(file.size / 1024))} KB`
      const isPdf = file.name.toLowerCase().endsWith('.pdf')
      const newDoc: MedicalDocument = {
        id: `doc-${Date.now()}`,
        title: file.name,
        type: isPdf ? 'prescription' : 'lab_report',
        date: 'Today',
        size: formattedSize,
        status: 'verified',
      }
      addDocument(newDoc)
    }
  }

  return (
    <div className="flex flex-col items-center justify-between h-full max-w-4xl w-full mx-auto px-6 py-1 select-none">
      {/* Hidden browser file input for Upload from PC */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept=".pdf,.jpg,.jpeg,.png"
        className="hidden"
      />

      {/* Heading - Desktop First */}
      <div className="text-center my-2 max-w-2xl">
        <h2 className="text-3xl sm:text-4xl font-bold text-[#243331] mb-2 tracking-tight">
          {t.page7_documents.title}
        </h2>
        <p className="text-base sm:text-lg text-[#647471] font-medium">
          {t.page7_documents.subtitle}
        </p>
      </div>

      {/* Main Scanner & Upload Card (Desktop-First Wide Card) */}
      <div className="w-full flex-1 min-h-0 overflow-y-auto my-1 pr-1">
        <div className="w-full bg-[#FFFFFF] border-2 border-dashed border-[#D9E2DF] hover:border-[#2F7D73] rounded-3xl p-6 sm:p-8 text-center transition-all">
          {/* Document Icon in soft blue */}
          <div className="w-16 h-16 rounded-2xl bg-[#EFF6FF] text-[#2563EB] flex items-center justify-center mx-auto mb-3 shadow-xs">
            <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>

          <h3 className="text-xl sm:text-2xl font-bold text-[#243331] mb-1">
            {t.page7_documents.cardTitle}
          </h3>
          <p className="text-sm text-[#647471] mb-2">
            {t.page7_documents.cardSubtitle}
          </p>
          <span className="inline-block text-xs font-semibold px-3 py-1 bg-[#F6F8F7] text-[#647471] rounded-full border border-[#D9E2DF]">
            {t.page7_documents.supportedFormats}
          </span>

          {/* 3 Action Buttons: Scanner, PC Upload, USB */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mt-6">
            {/* 1. Use Scanner Button */}
            <button
              type="button"
              onClick={handleSimulateScanner}
              disabled={isScanning}
              className="py-4 px-4 bg-[#FFFFFF] border-2 border-[#D9E2DF] hover:border-[#2F7D73] hover:bg-[#F9FBFA] active:bg-[#DCEDEA] text-[#243331] font-bold rounded-2xl flex items-center justify-center gap-2.5 shadow-xs transition-all cursor-pointer disabled:opacity-50"
            >
              <svg className="w-5 h-5 text-[#2F7D73]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" />
              </svg>
              <span>{t.page7_documents.useScanner}</span>
            </button>

            {/* 2. Upload from PC (Item 9: Native file picker) */}
            <button
              type="button"
              onClick={handleTriggerPCUpload}
              disabled={isScanning}
              className="py-4 px-4 bg-[#FFFFFF] border-2 border-[#2F7D73] bg-[#E8F4F1] hover:bg-[#DCEDEA] text-[#2F7D73] font-bold rounded-2xl flex items-center justify-center gap-2.5 shadow-xs transition-all cursor-pointer disabled:opacity-50"
            >
              <svg className="w-5 h-5 text-[#2F7D73]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
              <span>{t.page7_documents.uploadPC}</span>
            </button>

            {/* 3. Upload from USB Button */}
            <button
              type="button"
              onClick={handleSimulateUSB}
              disabled={isScanning}
              className="py-4 px-4 bg-[#FFFFFF] border-2 border-[#D9E2DF] hover:border-[#2563EB] hover:bg-[#F9FBFA] active:bg-[#EFF6FF] text-[#243331] font-bold rounded-2xl flex items-center justify-center gap-2.5 shadow-xs transition-all cursor-pointer disabled:opacity-50"
            >
              <svg className="w-5 h-5 text-[#2563EB]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 9l4-4 4 4m0 6l-4 4-4-4" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 5v14" />
              </svg>
              <span>{t.page7_documents.uploadUSB}</span>
            </button>
          </div>

          {/* Scanner Activity Indicator */}
          {isScanning && (
            <div className="mt-4 p-3 bg-[#EFF6FF] text-[#1D4ED8] rounded-xl text-sm font-medium flex items-center justify-center gap-2 animate-pulse">
              <div className="w-4 h-4 border-2 border-[#1D4ED8] border-t-transparent rounded-full animate-spin" />
              <span>{scanProgress}</span>
            </div>
          )}
        </div>

        {/* Uploaded Documents List */}
        {documents.length > 0 && (
          <div className="mt-4 space-y-2">
            <p className="text-xs font-bold uppercase tracking-wider text-[#647471] px-1">
              {t.page7_documents.uploadedTitle} ({documents.length}):
            </p>
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="flex items-center justify-between p-3.5 bg-white border border-[#D9E2DF] rounded-2xl shadow-xs"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-[#DCEDEA] text-[#2F7D73] flex items-center justify-center flex-shrink-0">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <div>
                    <p className="text-sm font-bold text-[#243331]">{doc.title}</p>
                    <p className="text-xs text-[#647471]">{doc.date} • {doc.size}</p>
                  </div>
                </div>
                <span className="text-xs font-semibold px-2.5 py-1 bg-[#EBF4EE] text-[#4F8A6D] rounded-lg">
                  ✓ {t.common.ready}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Bottom Bar: Back + Hear Again + Next */}
      <div className="w-full flex items-center justify-between mt-auto pt-3 border-t border-[#D9E2DF]">
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
          onClick={() => goTo('review')}
          className="px-8 py-3.5 bg-[#4F8A6D] hover:bg-[#3E6E56] active:bg-[#335B47] text-white font-bold text-base rounded-xl shadow-md flex items-center gap-2 transition-all cursor-pointer min-h-[48px]"
        >
          <span>{t.common.next}</span>
          <svg className="w-5 h-5 stroke-current stroke-2" fill="none" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
          </svg>
        </button>
      </div>
    </div>
  )
}

