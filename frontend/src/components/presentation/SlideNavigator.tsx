import React from 'react'
import { ChevronLeft, ChevronRight } from '@mui/icons-material'
import { cn } from '@/lib/utils'

interface SlideNavigatorProps {
  currentSlide: number
  totalSlides: number
  onNavigate: (slideNumber: number) => void
}

export const SlideNavigator: React.FC<SlideNavigatorProps> = ({
  currentSlide,
  totalSlides,
  onNavigate
}) => {
  const handlePrevious = () => {
    if (currentSlide > 1) {
      onNavigate(currentSlide - 1)
    }
  }

  const handleNext = () => {
    if (currentSlide < totalSlides) {
      onNavigate(currentSlide + 1)
    }
  }

  return (
    <div className="flex items-center gap-4">
      <button
        onClick={handlePrevious}
        disabled={currentSlide === 1}
        className={cn(
          'p-2 rounded-lg transition-colors',
          currentSlide === 1
            ? 'text-text-muted cursor-not-allowed opacity-50'
            : 'text-text hover:bg-primary/10'
        )}
      >
        <ChevronLeft className="w-5 h-5" />
      </button>

      <div className="text-text">
        <span className="font-medium">{currentSlide}</span>
        <span className="text-text-muted mx-2">/</span>
        <span className="text-text-muted">{totalSlides}</span>
      </div>

      <button
        onClick={handleNext}
        disabled={currentSlide === totalSlides}
        className={cn(
          'p-2 rounded-lg transition-colors',
          currentSlide === totalSlides
            ? 'text-text-muted cursor-not-allowed opacity-50'
            : 'text-text hover:bg-primary/10'
        )}
      >
        <ChevronRight className="w-5 h-5" />
      </button>
    </div>
  )
}