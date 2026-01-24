import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { HugeiconsIcon } from '@hugeicons/react'
import { Cancel01Icon } from '@hugeicons/core-free-icons'
import { cn } from '@/lib/utils'

interface FirstTimeTooltipProps {
  id: string
  children: React.ReactNode
  content: string
  position?: 'top' | 'bottom' | 'left' | 'right'
  className?: string
}

const STORAGE_KEY = 'ppt-ai-dismissed-tooltips'

function getDismissedTooltips(): string[] {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    return stored ? JSON.parse(stored) : []
  } catch {
    return []
  }
}

function dismissTooltip(id: string): void {
  try {
    const dismissed = getDismissedTooltips()
    if (!dismissed.includes(id)) {
      dismissed.push(id)
      localStorage.setItem(STORAGE_KEY, JSON.stringify(dismissed))
    }
  } catch {
  }
}

export const FirstTimeTooltip: React.FC<FirstTimeTooltipProps> = ({
  id,
  children,
  content,
  position = 'top',
  className
}) => {
  const [isVisible, setIsVisible] = useState(false)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const dismissed = getDismissedTooltips()
    if (!dismissed.includes(id)) {
      const timer = setTimeout(() => setIsVisible(true), 500)
      return () => clearTimeout(timer)
    }
  }, [id])

  const handleDismiss = () => {
    setIsVisible(false)
    dismissTooltip(id)
  }

  const positionClasses = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2'
  }

  const arrowClasses = {
    top: 'top-full left-1/2 -translate-x-1/2 border-t-primary border-x-transparent border-b-transparent',
    bottom: 'bottom-full left-1/2 -translate-x-1/2 border-b-primary border-x-transparent border-t-transparent',
    left: 'left-full top-1/2 -translate-y-1/2 border-l-primary border-y-transparent border-r-transparent',
    right: 'right-full top-1/2 -translate-y-1/2 border-r-primary border-y-transparent border-l-transparent'
  }

  return (
    <div ref={containerRef} className={cn('relative inline-block', className)}>
      {children}
      
      <AnimatePresence>
        {isVisible && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.2 }}
            className={cn(
              'absolute z-50 w-56',
              positionClasses[position]
            )}
          >
            <div className="bg-primary text-primary-foreground rounded-md p-3 shadow-lg text-sm">
              <div className="flex items-start gap-2">
                <p className="flex-1 leading-relaxed">{content}</p>
                <button
                  onClick={handleDismiss}
                  className="flex-shrink-0 p-0.5 rounded hover:bg-primary-foreground/20 transition-colors"
                  aria-label="Dismiss tooltip"
                >
                  <HugeiconsIcon icon={Cancel01Icon} size={14} />
                </button>
              </div>
            </div>
            <div 
              className={cn(
                'absolute w-0 h-0 border-4',
                arrowClasses[position]
              )}
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export function resetAllTooltips(): void {
  try {
    localStorage.removeItem(STORAGE_KEY)
  } catch {
  }
}
