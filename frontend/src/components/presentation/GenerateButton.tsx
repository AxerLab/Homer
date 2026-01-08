import React, { useState, useRef, useEffect } from 'react'
import { Send, AutoStories } from '@mui/icons-material'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/lib/utils'

interface GenerateButtonProps {
  onGenerate: (prompt: string, format: 'PPTX' | 'TeX', theme?: string, useRag?: boolean) => void
  isGenerating?: boolean
  isSidebarOpen?: boolean
}

export const GenerateButton: React.FC<GenerateButtonProps> = ({
  onGenerate,
  isGenerating = false,
}) => {
  const [prompt, setPrompt] = useState('')
  const [isExpanded, setIsExpanded] = useState(false)
  const [selectedFormat, setSelectedFormat] = useState<'PPTX' | 'TeX'>('PPTX')
  const [selectedTheme, setSelectedTheme] = useState<string>('default')
  const [useRag, setUseRag] = useState(false)
  const dialogRef = useRef<HTMLDivElement>(null)

  // Click outside handler
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dialogRef.current && !dialogRef.current.contains(event.target as Node)) {
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
              'px-8 py-4 bg-primary text-white rounded-xl font-semibold shadow-lg transition-all animate-glow',
              'hover:bg-primary/90 hover:shadow-xl',
              isGenerating && 'opacity-50 cursor-not-allowed'
            )}
          >
            {isGenerating ? 'Generating...' : 'Generate...'}
          </motion.button>
        ) : (
          <motion.div
            ref={dialogRef}
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: 20 }}
            className="relative"
          >
            <div className="bg-elevated/95 backdrop-blur-xl border border-primary/30 rounded-2xl p-6 shadow-2xl min-w-[500px]">
              <div className="before:absolute before:inset-0 before:-z-10 before:rounded-2xl before:bg-gradient-to-r before:from-primary/20 before:to-primary/10 before:blur-xl" />

              <textarea
                autoFocus
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe your presentation..."
                className="w-full h-24 bg-background/50 border border-border rounded-lg px-4 py-3 text-text resize-none focus:outline-none focus:border-primary/50 placeholder:text-text-muted/50"
              />

              <div className="mt-4 flex items-center justify-between gap-4">
                <div className="flex flex-col gap-1">
                  <div className="flex items-center gap-2 text-sm font-medium text-text">
                    <AutoStories className="w-4 h-4 text-primary" />
                    <span>Document Context</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-text-muted">
                    <span>Use uploaded docs for knowledge</span>
                    <span className="w-1 h-1 rounded-full bg-border" />
                    <a href="#/documents" className="hover:text-primary transition-colors hover:underline">Manage Library</a>
                  </div>
                </div>

                <button
                  type="button"
                  role="switch"
                  aria-checked={useRag}
                  onClick={() => setUseRag(!useRag)}
                  className={cn(
                    'relative w-11 h-6 rounded-full transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-primary/50',
                    useRag ? 'bg-primary shadow-[0_0_12px_rgba(99,102,241,0.4)]' : 'bg-background/50 border border-border'
                  )}
                >
                  <motion.div
                    initial={false}
                    animate={{ x: useRag ? 22 : 2 }}
                    transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                    className={cn(
                      'w-5 h-5 rounded-full shadow-md transition-colors',
                      useRag ? 'bg-white' : 'bg-text-muted/50'
                    )}
                  />
                </button>
              </div>

              <div className="flex items-center justify-between mt-4 gap-4">
                <div className="flex items-center gap-2 bg-background/50 rounded-full p-1">
                  {(['PPTX', 'TeX'] as const).map(format => (
                    <button
                      key={format}
                      onClick={() => setSelectedFormat(format)}
                      className={cn(
                        'px-4 py-1.5 rounded-full text-sm font-medium transition-all duration-200',
                        selectedFormat === format
                          ? 'bg-primary text-white shadow-lg'
                          : 'text-text-muted hover:text-text'
                      )}
                    >
                      {format}
                    </button>
                  ))}
                </div>

                {selectedFormat === 'PPTX' && (
                  <select
                    value={selectedTheme}
                    onChange={(e) => setSelectedTheme(e.target.value)}
                    className="px-3 py-1.5 bg-background/50 border border-border rounded-lg text-sm text-text focus:outline-none focus:border-primary/50"
                  >
                    <option value="default">Default</option>
                    <option value="dark">Dark</option>
                    <option value="light">Light</option>
                  </select>
                )}

                {prompt.trim() ? (
                  <button
                    onClick={handleGenerate}
                    className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
                  >
                    <Send className="w-4 h-4" />
                    Send
                  </button>
                ) : (
                  <button
                    onClick={handleClose}
                    className="text-text-muted hover:text-text transition-colors"
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