import React from 'react'

interface HeaderProps {
  presentationTitle?: string
}

export const Header: React.FC<HeaderProps> = ({
  presentationTitle = ''
}) => {
  return (
    <header className="h-16 bg-background border-b border-border flex items-center justify-between px-6">
      <div className="flex items-center gap-8 flex-1">
        <input
          type="text"
          value={presentationTitle}
          className="bg-transparent text-text text-lg font-medium focus:outline-none"
          placeholder="Select or generate a presentation"
          readOnly
        />
      </div>
    </header>
  )
}