import React from 'react'
import { motion } from 'framer-motion'
import { HugeiconsIcon } from '@hugeicons/react'
import { 
  Folder01Icon, 
  TextIcon, 
  PresentationBarChart01Icon,
  SparklesIcon
} from '@hugeicons/core-free-icons'
import { cn } from '@/lib/utils'
import { SimplifiedDocumentViewer } from '../viewer/SimplifiedDocumentViewer'
import { OnboardingFlow } from '../onboarding/OnboardingStep'
import type { Presentation } from '@/types/api'

interface SlideCanvasProps {
  presentation?: Presentation
  currentSlide?: number
  onSlideChange?: (slideNumber: number) => void
  documentCount?: number
  className?: string
}

const onboardingSteps = [
  {
    icon: <HugeiconsIcon icon={Folder01Icon} size={16} />,
    title: 'Add Your Documents',
    subtitle: 'Upload PDFs, docs, or notes to give AI your context',
    badge: 'Optional'
  },
  {
    icon: <HugeiconsIcon icon={TextIcon} size={16} />,
    title: 'Describe Your Topic',
    subtitle: 'Tell AI what presentation you need in natural language',
  },
  {
    icon: <HugeiconsIcon icon={PresentationBarChart01Icon} size={16} />,
    title: 'Get Your Slides',
    subtitle: 'AI generates a complete presentation in seconds',
  }
]

export const SlideCanvas: React.FC<SlideCanvasProps> = ({
  presentation,
  currentSlide = 1,
  onSlideChange,
  documentCount = 0,
  className
}) => {
  if (presentation?.id) {
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

  return (
    <div className={cn(
      'bg-gradient-to-b from-card to-background rounded-lg shadow-2xl aspect-[16/10] flex items-center justify-center p-8',
      className
    )}>
      <motion.div 
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="max-w-md w-full text-center"
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="mb-6"
        >
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-primary/10 flex items-center justify-center">
            <HugeiconsIcon icon={SparklesIcon} size={32} className="text-primary" />
          </div>
          <h2 className="text-xl font-semibold text-foreground mb-2">
            Create Your First Presentation
          </h2>
          <p className="text-sm text-muted-foreground">
            AI-powered slides from your ideas and documents
          </p>
        </motion.div>

        <OnboardingFlow 
          steps={onboardingSteps} 
          activeStep={0}
          completedSteps={documentCount > 0 ? [1] : []}
          className="text-left mb-6"
        />

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-center"
        >
          <a
            href="#/documents"
            className="text-sm text-muted-foreground hover:text-primary transition-colors"
          >
            {documentCount > 0 
              ? `${documentCount} document${documentCount > 1 ? 's' : ''} in library`
              : 'Or add documents first →'
            }
          </a>
        </motion.div>
      </motion.div>
    </div>
  )
}
