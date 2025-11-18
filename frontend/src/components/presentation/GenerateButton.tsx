import React, { useState, useRef, useEffect } from 'react'
import { cn } from '@/lib/utils'
import { motion, AnimatePresence } from 'framer-motion'
import { Send } from '@mui/icons-material'

interface GenerateButtonProps {
  onGenerate: (prompt: string, format: 'PPTX' | 'PDF' | 'TeX') => void
  isGenerating?: boolean
  isSidebarOpen: boolean
}

export const GenerateButton: React.FC<GenerateButtonProps> = ({
  onGenerate,
  isGenerating = false,
  isSidebarOpen
}) => {
  const [prompt, setPrompt] = useState('')
  const [isExpanded, setIsExpanded] = useState(false)
  const [hovering, setHovering] = useState(false)
  const [selectedFormat, setSelectedFormat] = useState<'PPTX' | 'PDF' | 'TeX'>('PPTX')
  const dialogRef = useRef<HTMLDivElement>(null)

  const handleGenerate = () => {
    if (prompt.trim()) {
      onGenerate(prompt, selectedFormat)
      setPrompt('')
      setIsExpanded(false)
    }
  }

  const handleClose = () => {
    setIsExpanded(false)
    setPrompt('')
  }

  // Handle click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dialogRef.current && !dialogRef.current.contains(event.target as Node)) {
        handleClose()
      }
    }

    if (isExpanded) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => {
        document.removeEventListener('mousedown', handleClickOutside)
      }
    }
  }, [isExpanded])

  return (
    <div
      className={cn(
        'fixed bottom-8 left-1/2 -translate-x-1/2 transition-all duration-300 z-10'
      )}
    >
      <AnimatePresence>
        {!isExpanded ? (
          <motion.button
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            onClick={() => setIsExpanded(true)}
            onMouseEnter={() => setHovering(true)}
            onMouseLeave={() => setHovering(false)}
            className={cn(
              'px-8 py-4 bg-primary text-white rounded-xl font-semibold',
              'hover:bg-primary/90 transition-all duration-300',
              'shadow-lg hover:shadow-xl',
              hovering && 'animate-glow'
            )}
            disabled={isGenerating}
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
            <div
              className={cn(
                'bg-elevated/95 backdrop-blur-xl border border-primary/30 rounded-2xl p-6',
                'shadow-2xl min-w-[500px]',
                'before:absolute before:inset-0 before:rounded-2xl before:bg-gradient-to-r',
                'before:from-primary/20 before:to-secondary/20 before:blur-3xl before:-z-10'
              )}
            >
              <textarea
                autoFocus
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault()
                    handleGenerate()
                  }
                }}
                placeholder="Describe your presentation..."
                className={cn(
                  'w-full h-24 bg-background/50 border border-border rounded-lg',
                  'px-4 py-3 text-text resize-none',
                  'focus:outline-none focus:border-primary/50',
                  'placeholder:text-text-muted'
                )}
              />

              <div className="flex items-center justify-between mt-4">
                {/* Format Selector Slider */}
                <div className="flex items-center gap-2 bg-background/50 rounded-full p-1">
                  {(['PPTX', 'PDF', 'TeX'] as const).map((format) => (
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

                {prompt.trim() ? (
                  <button
                    onClick={handleGenerate}
                    className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors text-sm font-medium"
                  >
                    <Send className="w-4 h-4" />
                    Send
                  </button>
                ) : (
                  <button
                    onClick={handleClose}
                    className="text-text-muted hover:text-text transition-colors text-sm"
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