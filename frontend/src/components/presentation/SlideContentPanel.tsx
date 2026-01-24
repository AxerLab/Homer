import React, { useState } from 'react'
import { HugeiconsIcon } from '@hugeicons/react'
import { SparklesIcon, SentIcon } from '@hugeicons/core-free-icons'
import { cn } from '@/lib/utils'
import { LoadingIndicator } from '@/components/ui/LoadingOverlay'
import { Card } from '@/components/ui/card'
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

  const currentSlide = slides[currentSlideNumber - 1]

  const handleSendModification = () => {
    if (modificationPrompt.trim() && onModifySlide) {
      onModifySlide(currentSlideNumber, modificationPrompt)
      setModificationPrompt('')
    }
  }

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
    <Card className={cn('border-l border-border flex flex-col h-full rounded-none', className)}>
      <div className="p-4 border-b border-border flex-none">
        <h3 className="text-lg font-medium text-foreground">
          {currentSlide?.title || `Slide ${currentSlideNumber}`}
        </h3>
        <div className="flex items-center gap-2 mt-1">
          <span className="text-xs text-muted-foreground">
            Slide {currentSlideNumber} of {totalSlides}
          </span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        <Card className="bg-muted/50 p-4 mb-4">
          <div className="text-sm text-muted-foreground whitespace-pre-wrap">
            {currentSlide?.content || 'No content available for this slide.'}
          </div>
        </Card>
        <div className="flex justify-end mt-6 mb-4 px-2">
          <button className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors">
            <HugeiconsIcon icon={SparklesIcon} size={12} />
            <span>AI Overview</span>
          </button>
        </div>
      </div>

      <div className="p-4 border-t border-border flex-none">
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
                'px-3 py-1 bg-primary/10 text-xs text-foreground/70 rounded-md hover:bg-primary/20 transition-colors',
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
            className="w-full bg-muted/50 border border-border rounded-md pl-4 pr-20 pt-3 pb-10 text-sm text-foreground resize-none focus:outline-none focus:border-primary/50"
            rows={2}
          />
          <div className="absolute right-2 bottom-2 flex items-center gap-2">
            <button
              onClick={handleSendModification}
              disabled={isModifying}
              className={cn(
                'p-1.5 bg-primary/20 hover:bg-primary/30 rounded-md transition-colors',
                isModifying && 'opacity-50 cursor-not-allowed'
              )}
            >
              <HugeiconsIcon icon={SentIcon} size={16} className="text-primary" />
            </button>
          </div>
        </div>
      </div>
    </Card>
  )
}
