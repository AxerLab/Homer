import React from 'react'
import { ChevronLeft, ChevronRight } from '@mui/icons-material'
import { cn } from '@/lib/utils'
import { PastChat } from '@/types/presentation'

interface SidebarProps {
  isOpen: boolean
  onToggle: () => void
  pastChats: PastChat[]
  selectedChatId?: string
  onChatSelect: (chatId: string) => void
}

export const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  onToggle,
  pastChats,
  selectedChatId,
  onChatSelect,
}) => {
  return (
    <>
      {/* Sidebar */}
      <div
        className={cn(
          'fixed left-0 top-0 h-full bg-elevated border-r border-border transition-all duration-300 z-20',
          isOpen ? 'w-64' : 'w-0'
        )}
      >
        {isOpen && (
          <div className="flex flex-col h-full p-4">
            <h2 className="text-lg font-semibold mb-4 text-text">Past Chats</h2>
            <div className="flex-1 overflow-y-auto">
              <div className="space-y-2">
                {pastChats.map((chat) => (
                  <button
                    key={chat.id}
                    onClick={() => onChatSelect(chat.id)}
                    className={cn(
                      'w-full text-left px-4 py-3 rounded-lg transition-colors',
                      'hover:bg-primary/10 text-text-muted hover:text-text',
                      selectedChatId === chat.id && 'bg-primary/20 text-text'
                    )}
                  >
                    <div className="font-medium truncate">{chat.title}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Toggle Button */}
      <button
        onClick={onToggle}
        className={cn(
          'fixed top-20 z-30 bg-elevated border border-border rounded-r-lg p-2',
          'hover:bg-primary/10 transition-all duration-300',
          isOpen ? 'left-64' : 'left-0 rounded-l-lg'
        )}
      >
        {isOpen ? (
          <ChevronLeft className="text-text w-5 h-5" />
        ) : (
          <ChevronRight className="text-text w-5 h-5" />
        )}
      </button>
    </>
  )
}