import React, { useState, useRef, useEffect, useCallback } from 'react'
import { HugeiconsIcon } from '@hugeicons/react'
import { SentIcon, BookOpen01Icon, Folder01Icon } from '@hugeicons/core-free-icons'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/lib/utils'
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { DocumentUploadInline } from '@/components/rag/DocumentUploadInline'
import { ragApi } from '@/services/api'

interface GenerateButtonProps {
  onGenerate: (prompt: string, format: 'PPTX' | 'TeX', theme?: string, useRag?: boolean) => void
  isGenerating?: boolean
  documentCount?: number
  onDocumentCountChange?: () => void
}

export const GenerateButton: React.FC<GenerateButtonProps> = ({
  onGenerate,
  isGenerating = false,
  documentCount: externalDocCount,
  onDocumentCountChange,
}) => {
  const [prompt, setPrompt] = useState('')
  const [isExpanded, setIsExpanded] = useState(false)
  const [selectedFormat, setSelectedFormat] = useState<'PPTX' | 'TeX'>('PPTX')
  const [selectedTheme, setSelectedTheme] = useState<string>('light')
  const [useRag, setUseRag] = useState(false)
  const [localDocCount, setLocalDocCount] = useState(0)
  const dialogRef = useRef<HTMLDivElement>(null)

  const documentCount = externalDocCount ?? localDocCount

  const fetchDocumentCount = useCallback(async () => {
    try {
      const response = await ragApi.listDocuments()
      const completedDocs = response.documents.filter(doc => doc.status === 'completed')
      setLocalDocCount(completedDocs.length)
    } catch {
      setLocalDocCount(0)
    }
  }, [])

  useEffect(() => {
    if (isExpanded && externalDocCount === undefined) {
      fetchDocumentCount()
    }
  }, [isExpanded, externalDocCount, fetchDocumentCount])

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement
      const isInsideDialog = dialogRef.current?.contains(target)
      const isInsideSelectPortal = target.closest('[data-radix-popper-content-wrapper]')
      
      if (!isInsideDialog && !isInsideSelectPortal) {
        setIsExpanded(false)
        setPrompt('')
      }
    }
    if (isExpanded) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isExpanded])

  const handleGenerate = () => {
    if (prompt.trim()) {
      onGenerate(prompt, selectedFormat, selectedFormat === 'PPTX' ? selectedTheme : undefined, useRag)
      setPrompt('')
      setIsExpanded(false)
    }
  }

  const handleClose = () => {
    setIsExpanded(false)
    setPrompt('')
  }

  const handleUploadComplete = () => {
    fetchDocumentCount()
    onDocumentCountChange?.()
    // Don't auto-enable RAG - document is still processing at this point
    // User can manually enable once document status is 'completed'
  }

  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 transition-all duration-300 z-50">
      <AnimatePresence>
        {!isExpanded ? (
          <motion.button
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            onClick={() => setIsExpanded(true)}
            disabled={isGenerating}
            className={cn(
              'flex items-center gap-2 px-8 py-4 bg-primary text-primary-foreground rounded-md font-semibold shadow-lg transition-all animate-glow',
              'hover:bg-primary/90 hover:shadow-xl',
              isGenerating && 'opacity-50 cursor-not-allowed'
            )}
          >
            {isGenerating ? 'Generating...' : 'Generate...'}
            {documentCount > 0 && !isGenerating && (
              <Badge variant="secondary" className="ml-1 bg-primary-foreground/20 text-primary-foreground">
                {documentCount} doc{documentCount > 1 ? 's' : ''}
              </Badge>
            )}
          </motion.button>
        ) : (
          <motion.div
            ref={dialogRef}
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            className="relative"
          >
            <div className="bg-card/95 backdrop-blur-xl border border-primary/30 rounded-lg p-6 shadow-2xl min-w-[500px]">
              <div className="before:absolute before:inset-0 before:-z-10 before:rounded-lg before:bg-gradient-to-r before:from-primary/20 before:to-primary/10 before:blur-xl" />

              <textarea
                autoFocus
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe your presentation..."
                className="w-full h-24 bg-background/50 border border-border rounded-md px-4 py-3 text-foreground resize-none focus:outline-none focus:border-primary/50 placeholder:text-muted-foreground/50"
              />

              <div className="mt-4 p-3 rounded-md bg-muted/30 border border-border">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <HugeiconsIcon icon={BookOpen01Icon} size={18} className="text-primary" />
                    <span className="font-medium text-sm text-foreground">Knowledge Base</span>
                    {documentCount > 0 && (
                      <Badge variant="secondary" className="text-xs">
                        {documentCount} doc{documentCount > 1 ? 's' : ''}
                      </Badge>
                    )}
                  </div>
                  <Switch
                    checked={useRag}
                    onCheckedChange={setUseRag}
                    disabled={documentCount === 0}
                    className="data-[state=checked]:bg-primary"
                  />
                </div>

                {documentCount === 0 ? (
                  <div className="mt-3">
                    <p className="text-xs text-muted-foreground mb-2">
                      Upload documents to give AI your context
                    </p>
                    <DocumentUploadInline onUploadComplete={handleUploadComplete} />
                  </div>
                ) : (
                  <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
                    <span>
                      {useRag 
                        ? 'AI will use your documents as reference' 
                        : 'Toggle on to use your documents'}
                    </span>
                    <a 
                      href="#/documents" 
                      className="flex items-center gap-1 hover:text-primary transition-colors"
                    >
                      <HugeiconsIcon icon={Folder01Icon} size={12} />
                      Manage
                    </a>
                  </div>
                )}
              </div>

              <div className="flex items-center justify-between mt-4 gap-4">
                <div className="flex items-center gap-1 bg-muted rounded-md p-1">
                  {(['PPTX', 'TeX'] as const).map(format => (
                    <button
                      key={format}
                      onClick={() => setSelectedFormat(format)}
                      className={cn(
                        'px-4 py-1.5 rounded-sm text-sm font-medium transition-all duration-200',
                        selectedFormat === format
                          ? 'bg-primary text-primary-foreground shadow-sm'
                          : 'text-muted-foreground hover:text-foreground'
                      )}
                    >
                      {format}
                    </button>
                  ))}
                </div>

                {selectedFormat === 'PPTX' && (
                  <Select value={selectedTheme} onValueChange={setSelectedTheme}>
                    <SelectTrigger className="w-28 h-9 bg-muted border-border">
                      <SelectValue placeholder="Theme" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="light">Light</SelectItem>
                      <SelectItem value="dark">Dark</SelectItem>
                      <SelectItem value="atlas">Atlas</SelectItem>
                    </SelectContent>
                  </Select>
                )}

                {prompt.trim() ? (
                  <button
                    onClick={handleGenerate}
                    className="flex items-center gap-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
                  >
                    <HugeiconsIcon icon={SentIcon} size={16} />
                    Send
                  </button>
                ) : (
                  <button
                    onClick={handleClose}
                    className="text-muted-foreground hover:text-foreground transition-colors"
                  >
                    Cancel
                  </button>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
