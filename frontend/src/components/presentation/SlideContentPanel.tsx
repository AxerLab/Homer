import React, { useState } from 'react'
import { AttachFile, AutoAwesome, Send } from '@mui/icons-material'
import { cn } from '@/lib/utils'
import { LoadingIndicator } from '@/components/ui/LoadingOverlay'
import type { SlideData } from '@/types/api'

interface SlideContentPanelProps {
  slides: SlideData[]
  currentSlideNumber: number
  totalSlides: number
  className?: string
  onModifySlide?: (slideNumber: number, prompt: string) => void
  isModifying?: boolean
}

export const SlideContentPanel: React.FC<SlideContentPanelProps> = ({
  slides,
  currentSlideNumber,
  totalSlides,
  className,
  onModifySlide,
  isModifying = false
}) => {
  const [modificationPrompt, setModificationPrompt] = useState('')

  // Get current slide data (1-indexed to 0-indexed)
  const currentSlide = slides[currentSlideNumber - 1]

  const handleSendModification = () => {
    if (modificationPrompt.trim() && onModifySlide) {
      onModifySlide(currentSlideNumber, modificationPrompt)
      setModificationPrompt('')
    }
  }

  // Map action buttons to descriptive instructions for the textarea
  const actionInstructions: Record<string, string> = {
    'Add Detail': 'Add more details and depth to this slide. Include specific examples, data points, or explanations.',
    'Simplify': 'Simplify the content of this slide. Make it more concise and easier to understand.',
    'Add Examples': 'Add concrete examples to illustrate the points made in this slide.',
    'Change tone': 'Change the tone of this slide to be more professional/casual/engaging.'
  }

  const handleQuickAction = (action: string) => {
    const instruction = actionInstructions[action] || action
    setModificationPrompt(instruction)
  }

  return (
    <div className={cn('bg-elevated border-l border-border flex flex-col h-full', className)}>
      <div className="p-4 border-b border-border flex-none">
        <h3 className="text-lg font-medium text-text">
          {currentSlide?.title || `Slide ${currentSlideNumber}`}
        </h3>
        <p className="text-xs text-text-muted mt-1">
          Slide {currentSlideNumber} of {totalSlides} • {currentSlide?.layout || 'unknown'} layout
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        <div className="bg-background/50 border border-border rounded-lg p-4 mb-4">
          <div className="text-sm text-text-muted whitespace-pre-wrap">
            {currentSlide?.content || 'No content available for this slide.'}
          </div>
        </div>
        <div className="flex justify-end mt-6 mb-4 px-2">
          <button className="flex items-center gap-1 text-xs text-text-muted hover:text-text">
            <AutoAwesome className="w-3 h-3" />
            <span>AI Overview</span>
          </button>
        </div>
      </div>

      <div className="p-4 border-t border-border flex-none">
        {/* Loading indicator when modifying */}
        <LoadingIndicator
          isVisible={isModifying}
          message="Updating slide..."
          className="mb-3"
        />

        <div className="flex flex-wrap gap-2 mb-3">
          {['Add Detail', 'Simplify', 'Add Examples', 'Change tone'].map(action => (
            <button
              key={action}
              onClick={() => handleQuickAction(action)}
              disabled={isModifying}
              className={cn(
                'px-3 py-1 bg-primary/10 text-xs text-text/70 rounded-full hover:bg-primary/20 transition-colors',
                isModifying && 'opacity-50 cursor-not-allowed'
              )}
            >
              {action}
            </button>
          ))}
        </div>
        <div className="relative">
          <textarea
            value={modificationPrompt}
            onChange={(e) => setModificationPrompt(e.target.value)}
            placeholder="Describe how you want to modify this slide..."
            className="w-full bg-background/50 border border-border rounded-lg pl-4 pr-20 pt-3 pb-10 text-sm text-text resize-none focus:outline-none focus:border-primary/50"
            rows={2}
          />
          <div className="absolute right-2 bottom-2 flex items-center gap-2">
            <button
              className={cn(
                'p-1.5 hover:bg-primary/10 rounded transition-colors',
                isModifying && 'opacity-50 cursor-not-allowed'
              )}
              disabled={isModifying}
            >
              <AttachFile className="w-4 h-4 text-text-muted" />
            </button>
            <button
              onClick={handleSendModification}
              disabled={isModifying}
              className={cn(
                'p-1.5 bg-primary/20 hover:bg-primary/30 rounded transition-colors',
                isModifying && 'opacity-50 cursor-not-allowed'
              )}
            >
              <Send className="w-4 h-4 text-primary" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}