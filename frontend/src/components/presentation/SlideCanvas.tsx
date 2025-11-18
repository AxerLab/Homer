import React from 'react'
import { cn } from '@/lib/utils'
import { Slide } from '@/types/presentation'

interface SlideCanvasProps {
  slide?: Slide
  className?: string
}

export const SlideCanvas: React.FC<SlideCanvasProps> = ({ slide, className }) => {
  return (
    <div
      className={cn(
        'bg-gradient-to-b from-gray-700 to-gray-800 rounded-lg shadow-2xl aspect-[16/10] flex items-center justify-center',
        className
      )}
    >
      {slide ? (
        <div className="p-8 w-full h-full flex flex-col">
          <h2 className="text-3xl font-bold text-white mb-4">{slide.title}</h2>
          <div className="text-lg text-gray-200 flex-1">
            {slide.content}
          </div>
        </div>
      ) : (
        <div className="text-gray-400 text-center">
          <p className="text-xl">No slide selected</p>
          <p className="text-sm mt-2">Generate or select a presentation to begin</p>
        </div>
      )}
    </div>
  )
}