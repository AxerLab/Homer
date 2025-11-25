import React from 'react'
import { ChevronLeft, ChevronRight, Delete } from '@mui/icons-material'
import { cn } from '@/lib/utils'
import type { PastChat } from '@/types'

interface SidebarProps {
  isOpen: boolean
  onToggle: () => void
  pastChats: PastChat[]
  selectedChatId?: string
  onChatSelect: (chatId: string) => void
  onChatDelete?: (chatId: string) => void
}

export const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  onToggle,
  pastChats,
  selectedChatId,
  onChatSelect,
  onChatDelete
}) => {
  return (
    <>
      <div className={cn(
        'fixed left-0 top-0 h-full bg-elevated border-r border-border transition-all duration-300 z-20',
        isOpen ? 'w-64' : 'w-0'
      )}>
        {isOpen && (
          <div className="flex flex-col h-full p-4">
            <h2 className="text-lg font-semibold mb-4 text-text">Past Chats</h2>
            <div className="flex-1 overflow-y-auto">
              <div className="space-y-2">
                {pastChats.map((chat) => (
                  <div
                    key={chat.id}
                    className={cn(
                      'group flex items-center gap-2 w-full px-4 py-3 rounded-lg transition-colors',
                      'hover:bg-primary/10',
                      selectedChatId === chat.id && 'bg-primary/20'
                    )}
                  >
                    <button
                      onClick={() => onChatSelect(chat.id)}
                      className={cn(
                        'flex-1 text-left truncate',
                        'text-text-muted hover:text-text',
                        selectedChatId === chat.id && 'text-text'
                      )}
                    >
                      <div className="font-medium truncate">{chat.title}</div>
                    </button>
                    {onChatDelete && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          onChatDelete(chat.id)
                        }}
                        className="opacity-0 group-hover:opacity-100 p-1 rounded hover:bg-red-500/20 text-text-muted hover:text-red-500 transition-all"
                        title="Delete presentation"
                      >
                        <Delete className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
      <button
        onClick={onToggle}
        className={cn(
          'fixed top-20 z-30 bg-elevated border border-border rounded-r-lg p-2',
          'hover:bg-primary/10 transition-all duration-300',
          isOpen ? 'left-64' : 'left-0 rounded-l-lg'
        )}
      >
        {isOpen ? <ChevronLeft className="text-text w-5 h-5" /> : <ChevronRight className="text-text w-5 h-5" />}
      </button>
    </>
  )
}