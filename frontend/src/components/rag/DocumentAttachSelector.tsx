import React, { useState, useEffect, useRef } from 'react'
import { AttachFile, CheckBox, CheckBoxOutlineBlank, OpenInNew } from '@mui/icons-material'
import { ragApi } from '@/services/api'
import type { RAGDocumentStatus } from '@/types/api'

interface DocumentAttachSelectorProps {
  selectedDocIds: string[]
  onSelectionChange: (docIds: string[]) => void
  className?: string
}

export const DocumentAttachSelector: React.FC<DocumentAttachSelectorProps> = ({
  selectedDocIds,
  onSelectionChange,
  className = ''
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const [documents, setDocuments] = useState<RAGDocumentStatus[]>([])
  const [loading, setLoading] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  useEffect(() => {
    if (isOpen) {
      setLoading(true)
      ragApi.listDocuments()
        .then(response => {
          setDocuments(response.documents.filter(doc => doc.status === 'completed'))
        })
        .catch(console.error)
        .finally(() => setLoading(false))
    }
  }, [isOpen])

  const toggleDocument = (docId: string) => {
    if (selectedDocIds.includes(docId)) {
      onSelectionChange(selectedDocIds.filter(id => id !== docId))
    } else {
      onSelectionChange([...selectedDocIds, docId])
    }
  }

  const selectedCount = selectedDocIds.length

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 bg-[#13131a] border border-[#1e293b] rounded-lg text-[#94a3b8] hover:border-[#6366f1]/50 hover:text-[#f8fafc] transition-colors"
      >
        <AttachFile className="w-4 h-4" />
        <span className="text-sm">Attach Documents</span>
        {selectedCount > 0 && (
          <span className="px-1.5 py-0.5 text-xs bg-[#6366f1] text-white rounded-full">
            {selectedCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 mt-2 w-72 bg-[#13131a] border border-[#1e293b] rounded-lg shadow-xl z-50">
          <div className="p-3 border-b border-[#1e293b]">
            <h4 className="text-sm font-medium text-[#f8fafc]">Select Documents</h4>
            <p className="text-xs text-[#94a3b8] mt-0.5">Choose context for generation</p>
          </div>

          <div className="max-h-64 overflow-y-auto">
            {loading ? (
              <div className="p-4 text-center">
                <div className="w-5 h-5 border-2 border-[#6366f1] border-t-transparent rounded-full animate-spin mx-auto" />
              </div>
            ) : documents.length === 0 ? (
              <div className="p-4 text-center text-[#94a3b8] text-sm">
                No completed documents available
              </div>
            ) : (
              <div className="py-1">
                {documents.map(doc => {
                  const isSelected = selectedDocIds.includes(doc.id)
                  return (
                    <button
                      key={doc.id}
                      type="button"
                      onClick={() => toggleDocument(doc.id)}
                      className="w-full flex items-center gap-3 px-3 py-2 hover:bg-[#1e293b] transition-colors"
                    >
                      {isSelected ? (
                        <CheckBox className="w-5 h-5 text-[#6366f1]" />
                      ) : (
                        <CheckBoxOutlineBlank className="w-5 h-5 text-[#94a3b8]" />
                      )}
                      <div className="flex-1 text-left min-w-0">
                        <p className="text-sm text-[#f8fafc] truncate">{doc.filename}</p>
                        <p className="text-xs text-[#94a3b8] uppercase">{doc.file_extension}</p>
                      </div>
                    </button>
                  )
                })}
              </div>
            )}
          </div>

          <div className="p-2 border-t border-[#1e293b]">
            <a
              href="#/documents"
              className="flex items-center justify-center gap-1 text-xs text-[#6366f1] hover:text-[#8b5cf6] transition-colors"
            >
              <span>Manage Documents</span>
              <OpenInNew className="w-3 h-3" />
            </a>
          </div>
        </div>
      )}
    </div>
  )
}
