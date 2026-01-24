import React from 'react'
import { PanelLeftClose, PanelLeftOpen } from 'lucide-react'
import { FirstTimeTooltip } from '@/components/ui/FirstTimeTooltip'
import { cn } from '@/lib/utils'

interface HeaderProps {
  presentationTitle?: string
  isSidebarOpen?: boolean
  onToggleSidebar?: () => void
}

export const Header: React.FC<HeaderProps> = ({
  presentationTitle = '',
  isSidebarOpen = true,
  onToggleSidebar
}) => {
  return (
    <header className="h-16 bg-background border-b border-border flex items-center justify-between px-6">
      <div className="flex items-center gap-4 flex-1">
        {onToggleSidebar && (
          <FirstTimeTooltip
            id="sidebar-toggle-hint"
            content="Press ⌘B (Mac) or Ctrl+B (Windows) to toggle the sidebar"
            position="bottom"
          >
            <button
              onClick={onToggleSidebar}
              className={cn(
                'p-2 -ml-2 rounded-md transition-colors',
                'text-muted-foreground hover:text-foreground hover:bg-muted',
                'focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-background'
              )}
              aria-label={isSidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
              aria-expanded={isSidebarOpen}
              title={isSidebarOpen ? 'Collapse sidebar (⌘B)' : 'Expand sidebar (⌘B)'}
            >
              {isSidebarOpen ? (
                <PanelLeftClose size={20} />
              ) : (
                <PanelLeftOpen size={20} />
              )}
            </button>
          </FirstTimeTooltip>
        )}
        <h1 className="text-foreground text-lg font-medium truncate">
          {presentationTitle || 'Select or generate a presentation'}
        </h1>
      </div>
    </header>
  )
}
