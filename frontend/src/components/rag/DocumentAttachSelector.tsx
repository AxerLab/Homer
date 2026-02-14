import React, { useState, useEffect, useRef } from 'react'
import { HugeiconsIcon } from '@hugeicons/react'
import { 
  Attachment01Icon, 
  CheckmarkSquare01Icon, 
  SquareIcon, 
  ArrowUpRight01Icon 
} from '@hugeicons/core-free-icons'
import { ragApi } from '@/services/api'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import type { RAGDocumentStatus } from '@/types/api'

interface DocumentAttachSelectorProps {
  selectedDocIds: string[]
  onSelectionChange: (docIds: string[]) => void
  className?: string
  dropdownPlacement?: 'top' | 'bottom'
}

export const DocumentAttachSelector: React.FC<DocumentAttachSelectorProps> = ({
  selectedDocIds,
  onSelectionChange,
  className = '',
  dropdownPlacement = 'bottom'
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
        className="flex items-center gap-2 px-3 py-2 bg-card border border-border rounded-md text-muted-foreground hover:border-primary/50 hover:text-foreground transition-colors"
      >
        <HugeiconsIcon icon={Attachment01Icon} size={16} />
        <span className="text-sm">Attach Documents</span>
        {selectedCount > 0 && (
          <Badge className="px-1.5 py-0.5 text-xs">
            {selectedCount}
          </Badge>
        )}
      </button>

      {isOpen && (
        <Card className={`absolute left-0 w-72 shadow-xl z-50 ${dropdownPlacement === 'top' ? 'bottom-full mb-2' : 'top-full mt-2'}`}>
          <div className="p-3 border-b border-border">
            <h4 className="text-sm font-medium text-foreground">Select Documents</h4>
            <p className="text-xs text-muted-foreground mt-0.5">Choose context for generation</p>
          </div>

          <div className="max-h-64 overflow-y-auto">
            {loading ? (
              <div className="p-4 text-center">
                <div className="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
              </div>
            ) : documents.length === 0 ? (
              <div className="p-4 text-center text-muted-foreground text-sm">
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
                      className="w-full flex items-center gap-3 px-3 py-2 hover:bg-muted transition-colors"
                    >
                      <HugeiconsIcon 
                        icon={isSelected ? CheckmarkSquare01Icon : SquareIcon} 
                        size={20} 
                        className={isSelected ? 'text-primary' : 'text-muted-foreground'} 
                      />
                      <div className="flex-1 text-left min-w-0">
                        <p className="text-sm text-foreground truncate">{doc.filename}</p>
                        <p className="text-xs text-muted-foreground uppercase">{doc.file_extension}</p>
                      </div>
                    </button>
                  )
                })}
              </div>
            )}
          </div>

          <div className="p-2 border-t border-border">
            <a
              href="#/documents"
              className="flex items-center justify-center gap-1 text-xs text-primary hover:text-secondary transition-colors"
            >
              <span>Manage Documents</span>
              <HugeiconsIcon icon={ArrowUpRight01Icon} size={12} />
            </a>
          </div>
        </Card>
      )}
    </div>
  )
}
