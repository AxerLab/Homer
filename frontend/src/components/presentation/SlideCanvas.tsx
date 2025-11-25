import React from 'react'
import { cn } from '@/lib/utils'
import { SimplifiedDocumentViewer } from '../viewer/SimplifiedDocumentViewer'
import type { Presentation } from '@/types/api'

interface SlideCanvasProps {
  presentation?: Presentation
  currentSlide?: number
  onSlideChange?: (slideNumber: number) => void
  className?: string
}

export const SlideCanvas: React.FC<SlideCanvasProps> = ({
  presentation,
  currentSlide = 1,
  onSlideChange,
  className
}) => {
  // If we have a presentation with a generated file, show the viewer
  if (presentation?.id) {
    // Use the file_type from the presentation, defaulting to 'pdf' if not specified
    const fileType = presentation.file_type || 'pdf'

    return (
      <SimplifiedDocumentViewer
        presentation={presentation}
        fileType={fileType}
        currentPage={currentSlide}
        onPageChange={onSlideChange}
        className={cn('rounded-lg shadow-2xl', className)}
      />
    )
  }

  // Show placeholder when no presentation is selected
  return (
    <div className={cn(
      'bg-gradient-to-b from-gray-700 to-gray-800 rounded-lg shadow-2xl aspect-[16/10] flex items-center justify-center',
      className
    )}>
      <div className="text-gray-400 text-center">
        <p className="text-xl">No presentation selected</p>
        <p className="text-sm mt-2">Select a presentation from Past Chats or generate a new one</p>
      </div>
    </div>
  )
}