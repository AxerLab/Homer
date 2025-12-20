import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/lib/utils'

interface LoadingOverlayProps {
    isVisible: boolean
    message?: string
    className?: string
    variant?: 'fullscreen' | 'inline'
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
    isVisible,
    message = 'Generating...',
    className,
    variant = 'fullscreen'
}) => {
    return (
        <AnimatePresence>
            {isVisible && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className={cn(
                        variant === 'fullscreen'
                            ? 'fixed inset-0 z-50 flex items-center justify-center'
                            : 'absolute inset-0 z-10 flex items-center justify-center',
                        'bg-background/80 backdrop-blur-sm',
                        className
                    )}
                >
                    <motion.div
                        initial={{ scale: 0.95, opacity: 0, y: 10 }}
                        animate={{ scale: 1, opacity: 1, y: 0 }}
                        exit={{ scale: 0.95, opacity: 0, y: 10 }}
                        transition={{ duration: 0.2 }}
                        className="flex flex-col items-center gap-6 p-8"
                    >
                        {/* Minimalist Spinner */}
                        <div className="relative w-12 h-12">
                            <motion.div
                                className="absolute inset-0 rounded-full border-[3px] border-primary/20"
                            />
                            <motion.div
                                className="absolute inset-0 rounded-full border-[3px] border-primary border-t-transparent"
                                animate={{ rotate: 360 }}
                                transition={{
                                    duration: 1,
                                    repeat: Infinity,
                                    ease: "linear"
                                }}
                            />
                        </div>

                        {/* Message */}
                        <div className="flex flex-col items-center gap-2">
                            <motion.h3
                                initial={{ opacity: 0, y: 5 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ delay: 0.1 }}
                                className="text-lg font-medium text-text tracking-tight"
                            >
                                {message}
                            </motion.h3>
                            <motion.p
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 0.5 }}
                                transition={{ delay: 0.2 }}
                                className="text-sm text-text-muted font-light"
                            >
                                This may take a moment
                            </motion.p>
                        </div>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    )
}

// Smaller inline loading indicator for panels
export const LoadingIndicator: React.FC<{
    isVisible: boolean
    message?: string
    className?: string
}> = ({ isVisible, message = 'Processing...', className }) => {
    return (
        <AnimatePresence>
            {isVisible && (
                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.2 }}
                    className={cn(
                        'flex items-center gap-3 p-4 rounded-lg bg-primary/10 border border-primary/30',
                        className
                    )}
                >
                    {/* Small spinning ring */}
                    <div className="relative w-5 h-5 flex-shrink-0">
                        <motion.div
                            className="absolute inset-0 rounded-full border-2 border-transparent border-t-primary border-r-primary/50"
                            animate={{ rotate: 360 }}
                            transition={{
                                duration: 0.8,
                                repeat: Infinity,
                                ease: 'linear'
                            }}
                        />
                    </div>

                    <span className="text-sm text-primary font-medium">{message}</span>
                </motion.div>
            )}
        </AnimatePresence>
    )
}
