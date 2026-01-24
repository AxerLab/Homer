import React from 'react'
import { HugeiconsIcon } from '@hugeicons/react'
import { 
  Delete01Icon, 
  Folder01Icon,
  Add01Icon,
  PresentationBarChart01Icon,
  File02Icon
} from '@hugeicons/core-free-icons'
import { motion, AnimatePresence } from 'framer-motion'
import { cn } from '@/lib/utils'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'
import type { PastChat } from '@/types'

const formatRelativeTime = (date: Date | string): string => {
  const now = new Date()
  const dateObj = new Date(date)
  const diff = now.getTime() - dateObj.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return 'Just now'
  if (minutes < 60) return `${minutes}m ago`
  if (hours < 24) return `${hours}h ago`
  if (days < 7) return `${days}d ago`
  return dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

interface SidebarProps {
  isOpen: boolean
  onToggle: () => void
  pastChats: PastChat[]
  selectedChatId?: string
  onChatSelect: (chatId: string) => void
  onChatDelete?: (chatId: string) => void
  documentCount?: number
}

export const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  onToggle,
  pastChats,
  selectedChatId,
  onChatSelect,
  onChatDelete,
  documentCount = 0
}) => {
  return (
    <>
      <motion.div 
        initial={false}
        animate={{ width: isOpen ? 256 : 0 }}
        transition={{ duration: 0.3, ease: "easeInOut" }}
        className={cn(
          'fixed left-0 top-0 h-full bg-card border-r border-border z-20 overflow-hidden'
        )}
      >
        <AnimatePresence>
          {isOpen && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="flex flex-col h-full"
            >
              <div className="p-4 pb-2">
                <div className="flex items-center gap-2 mb-4 text-foreground">
                  <HugeiconsIcon icon={PresentationBarChart01Icon} size={20} className="text-primary" />
                  <h2 className="text-lg font-semibold">Your Slides</h2>
                </div>
              </div>

              <div className="flex-1 overflow-y-auto px-2">
                {pastChats.length === 0 ? (
                  <div className="flex flex-col items-center justify-center h-32 text-muted-foreground">
                    <HugeiconsIcon icon={File02Icon} size={24} className="mb-2 opacity-50" />
                    <span className="text-sm">No presentations yet</span>
                  </div>
                ) : (
                  <div className="space-y-1">
                    {pastChats.map((chat, index) => (
                      <motion.div
                        key={chat.id}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.02 }}
                        className={cn(
                          'group flex items-center gap-2 w-full px-3 py-2.5 rounded-r-md transition-all border-l-2',
                          selectedChatId === chat.id 
                            ? 'bg-primary/10 border-primary' 
                            : 'border-transparent hover:bg-muted/60 hover:border-muted-foreground/20'
                        )}
                      >
                        <button
                          onClick={() => onChatSelect(chat.id)}
                          className="flex-1 text-left min-w-0"
                        >
                          <div className={cn(
                            "font-medium truncate text-sm transition-colors",
                            selectedChatId === chat.id ? "text-foreground" : "text-muted-foreground group-hover:text-foreground"
                          )}>
                            {chat.title}
                          </div>
                          {chat.timestamp && (
                            <div className="text-xs text-muted-foreground/60 mt-0.5">
                              {formatRelativeTime(chat.timestamp)}
                            </div>
                          )}
                        </button>
                        {onChatDelete && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              onChatDelete(chat.id)
                            }}
                            className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-destructive/20 text-muted-foreground hover:text-destructive transition-all"
                            title="Delete presentation"
                          >
                            <HugeiconsIcon icon={Delete01Icon} size={14} />
                          </button>
                        )}
                      </motion.div>
                    ))}
                  </div>
                )}
              </div>

              <div className="p-4 mt-auto">
                <Separator className="mb-4" />
                <a
                  href="#/documents"
                  className="flex items-center justify-between px-3 py-2.5 rounded-md hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <HugeiconsIcon icon={Folder01Icon} size={18} />
                    <span className="text-sm font-medium">Document Library</span>
                  </div>
                  {documentCount > 0 ? (
                    <Badge variant="secondary" className="text-xs">
                      {documentCount}
                    </Badge>
                  ) : (
                    <div className="flex items-center gap-1 text-xs text-primary">
                      <HugeiconsIcon icon={Add01Icon} size={12} />
                      <span>Add</span>
                    </div>
                  )}
                </a>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
      
      {/* Invisible rail for expanding sidebar when collapsed */}
      {!isOpen && (
        <button
          onClick={onToggle}
          className="fixed left-0 top-0 h-full w-1 z-20 group cursor-pointer"
          aria-label="Expand sidebar"
        >
          <div className="h-full w-full transition-all duration-200 group-hover:w-1 group-hover:bg-primary/40" />
        </button>
      )}
    </>
  )
}
