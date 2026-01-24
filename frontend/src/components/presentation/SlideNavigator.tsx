import React from 'react'
import { HugeiconsIcon } from '@hugeicons/react'
import { ArrowLeft01Icon, ArrowRight01Icon } from '@hugeicons/core-free-icons'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'

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
      <Button
        variant="ghost"
        size="icon"
        onClick={handlePrevious}
        disabled={currentSlide === 1}
        className={cn(
          currentSlide === 1 && 'text-muted-foreground opacity-50'
        )}
      >
        <HugeiconsIcon icon={ArrowLeft01Icon} size={20} />
      </Button>

      <div className="text-foreground">
        <span className="font-medium">{currentSlide}</span>
        <span className="text-muted-foreground mx-2">/</span>
        <span className="text-muted-foreground">{totalSlides}</span>
      </div>

      <Button
        variant="ghost"
        size="icon"
        onClick={handleNext}
        disabled={currentSlide === totalSlides}
        className={cn(
          currentSlide === totalSlides && 'text-muted-foreground opacity-50'
        )}
      >
        <HugeiconsIcon icon={ArrowRight01Icon} size={20} />
      </Button>
    </div>
  )
}
