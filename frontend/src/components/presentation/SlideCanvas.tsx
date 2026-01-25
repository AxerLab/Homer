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
import { ParticleBackground } from '../ui/ParticleBackground'
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
    icon: <HugeiconsIcon icon={Folder01Icon} size={20} />,
    title: 'Add Your Documents',
    subtitle: 'Upload PDFs, docs, or notes to give AI your context',
    badge: 'Optional'
  },
  {
    icon: <HugeiconsIcon icon={TextIcon} size={20} />,
    title: 'Describe Your Topic',
    subtitle: 'Tell AI what presentation you need in natural language',
  },
  {
    icon: <HugeiconsIcon icon={PresentationBarChart01Icon} size={20} />,
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
      'bg-gradient-to-b from-card to-background flex items-center justify-center p-8 w-full h-full relative overflow-hidden',
      className
    )}>
      <ParticleBackground className="absolute inset-0 pointer-events-none" />
      <motion.div 
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="max-w-2xl w-full text-center relative z-10"
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="mb-10"
        >
          <div className="w-24 h-24 mx-auto mb-6 rounded-full bg-[#1a1a2e] flex items-center justify-center">
            <HugeiconsIcon icon={SparklesIcon} size={48} className="text-primary" />
          </div>
          <h2 className="text-4xl font-semibold text-foreground mb-4">
            Create Your First Presentation
          </h2>
          <p className="text-lg text-muted-foreground">
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
            className="text-base text-muted-foreground hover:text-primary transition-colors"
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
