import React from 'react'
import { cn } from '@/lib/utils'
import { SlideNavigator } from '../presentation/SlideNavigator'

interface HeaderProps {
  currentSlide: number
  totalSlides: number
  onNavigate: (slideNumber: number) => void
  presentationTitle?: string
}

export const Header: React.FC<HeaderProps> = ({
  currentSlide,
  totalSlides,
  onNavigate,
  presentationTitle = 'Slide Title'
}) => {
  return (
    <header className="h-16 bg-background border-b border-border flex items-center justify-between px-6">
      <div className="flex items-center gap-8 flex-1">
        <input
          type="text"
          value={presentationTitle}
          className="bg-transparent text-text text-lg font-medium focus:outline-none"
          placeholder="Presentation Title"
          readOnly
        />
      </div>

      <div className="flex items-center gap-6">
        <SlideNavigator
          currentSlide={currentSlide}
          totalSlides={totalSlides}
          onNavigate={onNavigate}
        />
      </div>
    </header>
  )
}