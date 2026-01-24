import React from 'react'
import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

interface OnboardingStepProps {
  stepNumber: number
  icon: React.ReactNode
  title: string
  subtitle: string
  badge?: string
  isActive?: boolean
  isCompleted?: boolean
  className?: string
}

export const OnboardingStep: React.FC<OnboardingStepProps> = ({
  stepNumber,
  icon,
  title,
  subtitle,
  badge,
  isActive = false,
  isCompleted = false,
  className
}) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: stepNumber * 0.1, duration: 0.3 }}
      className={cn(
        'flex items-start gap-4 p-4 rounded-lg transition-all duration-200',
        isActive && 'bg-primary/10 border border-primary/30',
        isCompleted && 'opacity-60',
        !isActive && !isCompleted && 'bg-muted/30',
        className
      )}
    >
      <div
        className={cn(
          'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold transition-colors',
          isActive && 'bg-primary text-primary-foreground',
          isCompleted && 'bg-accent text-accent-foreground',
          !isActive && !isCompleted && 'bg-muted text-muted-foreground'
        )}
      >
        {isCompleted ? '✓' : stepNumber}
      </div>

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <div className={cn(
            'transition-colors',
            isActive ? 'text-primary' : 'text-muted-foreground'
          )}>
            {icon}
          </div>
          <h3 className={cn(
            'font-medium text-sm',
            isActive ? 'text-foreground' : 'text-muted-foreground'
          )}>
            {title}
          </h3>
          {badge && (
            <span className="text-xs text-muted-foreground/60 font-normal">
              ({badge})
            </span>
          )}
        </div>
        <p className="text-xs text-muted-foreground leading-relaxed">
          {subtitle}
        </p>
      </div>
    </motion.div>
  )
}

interface OnboardingFlowProps {
  steps: Array<{
    icon: React.ReactNode
    title: string
    subtitle: string
    badge?: string
  }>
  activeStep?: number
  completedSteps?: number[]
  className?: string
}

export const OnboardingFlow: React.FC<OnboardingFlowProps> = ({
  steps,
  activeStep = 1,
  completedSteps = [],
  className
}) => {
  return (
    <div className={cn('space-y-3', className)}>
      {steps.map((step, index) => (
        <OnboardingStep
          key={index}
          stepNumber={index + 1}
          icon={step.icon}
          title={step.title}
          subtitle={step.subtitle}
          badge={step.badge}
          isActive={activeStep === index + 1}
          isCompleted={completedSteps.includes(index + 1)}
        />
      ))}
    </div>
  )
}
