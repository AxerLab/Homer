import React, { useState } from 'react'
import { cn } from '@/lib/utils'
import { AttachFile, Send, AutoAwesome } from '@mui/icons-material'
import { Slide } from '@/types/presentation'

interface SlideContentPanelProps {
  slide?: Slide
  currentSlideNumber: number
  totalSlides: number
  className?: string
}

export const SlideContentPanel: React.FC<SlideContentPanelProps> = ({
  slide,
  currentSlideNumber,
  totalSlides,
  className
}) => {
  const [modificationPrompt, setModificationPrompt] = useState('')

  return (
    <div className={cn('bg-elevated border-l border-border flex flex-col h-full', className)}>
      {/* Header */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-text">
            {slide?.title || 'Slide Title'}
          </h3>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto p-4">
        {/* Slide Content Display */}
        <div className="bg-background/50 border border-border rounded-lg p-4 mb-4">
          <div className="text-sm text-text-muted mb-2">
            {slide?.content || `This slide provides an overview of artificial intelligence and its applications in modern technology.`}
          </div>
        </div>

        <div className="bg-background/50 border border-border rounded-lg p-4 text-sm text-text/80">
          Fusce nec rutrum velit. In vitae ex cursus, condimentum mi at, aliquet lorem. Integer ornare tellus augue, at lacinia elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer ornare tellus augue, in mauris non faucibus volutpat et velit ligula. Donec feugiat quam vel, aute mauris lacinia aliquam ornare. Sed finibus mauris non felis ultricies tincidunt. Fusce sem tellus, fringilla eget sapien sed, ornare maximus ligula.
        </div>

        {/* AI Overview Button - Middle Section */}
        <div className="flex justify-end mt-6 mb-4 px-2">
          <button className="flex items-center gap-1 text-xs text-text-muted hover:text-text transition-colors">
            <AutoAwesome className="w-3 h-3" />
            <span>AI Overview</span>
          </button>
        </div>
      </div>

      {/* Bottom Section - Quick Actions and Input */}
      <div className="p-4 border-t border-border">
        {/* Quick Action Chips */}
        <div className="flex flex-wrap gap-2 mb-3">
          <button className="px-3 py-1 bg-primary/10 text-xs text-text/70 rounded-full hover:bg-primary/20 transition-colors">
            Add Detail
          </button>
          <button className="px-3 py-1 bg-primary/10 text-xs text-text/70 rounded-full hover:bg-primary/20 transition-colors">
            Simplify
          </button>
          <button className="px-3 py-1 bg-primary/10 text-xs text-text/70 rounded-full hover:bg-primary/20 transition-colors">
            Add Examples
          </button>
          <button className="px-3 py-1 bg-primary/10 text-xs text-text/70 rounded-full hover:bg-primary/20 transition-colors">
            Change tone
          </button>
        </div>

        {/* Input Box with Attachment and Send */}
        <div className="relative">
          <textarea
            value={modificationPrompt}
            onChange={(e) => setModificationPrompt(e.target.value)}
            placeholder="Describe how you want to modify this slide..."
            className="w-full bg-background/50 border border-border rounded-lg pl-4 pr-20 pt-3 pb-10 text-sm text-text placeholder:text-text-muted/50 focus:outline-none focus:border-primary resize-none"
            rows={2}
          />
          <div className="absolute right-2 bottom-2 flex items-center gap-2">
            <button className="p-1.5 hover:bg-primary/10 rounded transition-colors">
              <AttachFile className="w-4 h-4 text-text-muted" />
            </button>
            <button className="p-1.5 bg-primary/20 hover:bg-primary/30 rounded transition-colors">
              <Send className="w-4 h-4 text-primary" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}