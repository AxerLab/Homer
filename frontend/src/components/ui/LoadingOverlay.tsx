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
    message = 'Loading...',
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
                    transition={{ duration: 0.2 }}
                    className={cn(
                        variant === 'fullscreen'
                            ? 'fixed inset-0 z-50 flex items-center justify-center'
                            : 'absolute inset-0 z-10 flex items-center justify-center',
                        'backdrop-blur-md bg-background/70',
                        className
                    )}
                >
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0.9, opacity: 0 }}
                        transition={{ duration: 0.2, delay: 0.1 }}
                        className="flex flex-col items-center gap-4 p-8 rounded-2xl bg-elevated/80 border border-border shadow-2xl"
                    >
                        {/* Animated spinner */}
                        <div className="relative w-16 h-16">
                            {/* Outer glowing ring */}
                            <div className="absolute inset-0 rounded-full bg-gradient-to-r from-primary to-secondary opacity-30 blur-lg animate-pulse" />

                            {/* Spinning ring */}
                            <div className="absolute inset-0 rounded-full border-4 border-border" />
                            <motion.div
                                className="absolute inset-0 rounded-full border-4 border-transparent border-t-primary border-r-secondary"
                                animate={{ rotate: 360 }}
                                transition={{
                                    duration: 1,
                                    repeat: Infinity,
                                    ease: 'linear'
                                }}
                            />

                            {/* Inner pulsing dot */}
                            <motion.div
                                className="absolute inset-4 rounded-full bg-gradient-to-br from-primary to-secondary"
                                animate={{
                                    scale: [0.8, 1, 0.8],
                                    opacity: [0.5, 1, 0.5]
                                }}
                                transition={{
                                    duration: 1.5,
                                    repeat: Infinity,
                                    ease: 'easeInOut'
                                }}
                            />
                        </div>

                        {/* Message */}
                        <motion.p
                            initial={{ y: 10, opacity: 0 }}
                            animate={{ y: 0, opacity: 1 }}
                            transition={{ delay: 0.2 }}
                            className="text-text font-medium text-center"
                        >
                            {message}
                        </motion.p>

                        {/* Animated dots */}
                        <div className="flex gap-1">
                            {[0, 1, 2].map((i) => (
                                <motion.div
                                    key={i}
                                    className="w-2 h-2 rounded-full bg-primary"
                                    animate={{
                                        y: [0, -6, 0],
                                        opacity: [0.4, 1, 0.4]
                                    }}
                                    transition={{
                                        duration: 0.8,
                                        repeat: Infinity,
                                        delay: i * 0.15,
                                        ease: 'easeInOut'
                                    }}
                                />
                            ))}
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
