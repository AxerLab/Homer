import React, { useState } from 'react'
import { AttachFile, AutoAwesome, Send } from '@mui/icons-material'
import { cn } from '@/lib/utils'
import type { Slide } from '@/types'

interface SlideContentPanelProps {
  slide?: Slide
  currentSlideNumber: number
  totalSlides: number
  className?: string
  onModifySlide?: (slideNumber: number, prompt: string) => void
}

export const SlideContentPanel: React.FC<SlideContentPanelProps> = ({
  slide,
  currentSlideNumber,
  className,
  onModifySlide
}) => {
  const [modificationPrompt, setModificationPrompt] = useState('')

  const handleSendModification = () => {
    if (modificationPrompt.trim() && onModifySlide) {
      onModifySlide(currentSlideNumber, modificationPrompt)
      setModificationPrompt('')
    }
  }

  return (
    <div className={cn('bg-elevated border-l border-border flex flex-col h-full', className)}>
      <div className="p-4 border-b border-border flex-none">
        <h3 className="text-lg font-medium text-text">{slide?.title || 'Slide Title'}</h3>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        <div className="bg-background/50 border border-border rounded-lg p-4 mb-4">
          <div className="text-sm text-text-muted mb-2">
            {slide?.content || 'This slide provides an overview of artificial intelligence and its applications in modern technology.'}
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
        <div className="flex flex-wrap gap-2 mb-3">
          {['Add Detail', 'Simplify', 'Add Examples', 'Change tone'].map(action => (
            <button
              key={action}
              className="px-3 py-1 bg-primary/10 text-xs text-text/70 rounded-full hover:bg-primary/20 transition-colors"
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
            <button className="p-1.5 hover:bg-primary/10 rounded transition-colors">
              <AttachFile className="w-4 h-4 text-text-muted" />
            </button>
            <button
              onClick={handleSendModification}
              className="p-1.5 bg-primary/20 hover:bg-primary/30 rounded transition-colors"
            >
              <Send className="w-4 h-4 text-primary" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}