# AI_FRONTEND_REPRODUCTION_SPEC_V1

## CRITICAL_CONTEXT_METADATA
- target_framework: React18_TypeScript_Vite
- styling_system: TailwindCSS_custom_config
- component_lib: MUI_icons_only
- animation_lib: framer-motion
- viewport: 1440x1024
- color_mode: dark_only
- browser_support: modern_evergreen

## EXACT_COLOR_PALETTE
```javascript
const COLORS_EXACT = {
  background: '#0a0a0f', // main_bg
  elevated: '#13131a', // sidebar_panels
  primary: '#6366f1', // buttons_accents
  secondary: '#8b5cf6', // unused_but_defined
  accent: '#14b8a6', // unused_but_defined
  text: '#f8fafc', // main_text
  'text-muted': '#94a3b8', // secondary_text
  border: '#1e293b', // all_borders
  destructive: '#ef4444', // unused_but_defined
  muted: '#1e293b', // same_as_border
  'muted-foreground': '#64748b' // tertiary_text
}
```

## PROJECT_STRUCTURE_EXACT
```
frontend/
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx
│   │   │   └── Header.tsx
│   │   └── presentation/
│   │       ├── SlideCanvas.tsx
│   │       ├── SlideContentPanel.tsx
│   │       ├── GenerateButton.tsx
│   │       └── SlideNavigator.tsx
│   ├── lib/
│   │   └── utils.ts
│   ├── types/
│   │   └── presentation.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── package.json
├── tailwind.config.ts
├── postcss.config.js
├── vite.config.ts
├── tsconfig.json
├── tsconfig.node.json
└── index.html
```

## PACKAGE_JSON_EXACT_DEPS
```json
{
  "dependencies": {
    "@emotion/react": "^11.11.0",
    "@emotion/styled": "^11.11.0",
    "@mui/material": "^5.15.0",
    "@mui/icons-material": "^5.15.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "framer-motion": "^11.2.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react": "^4.3.1",
    "autoprefixer": "^10.4.19",
    "postcss": "^8.4.38",
    "tailwindcss": "^3.4.3",
    "typescript": "^5.2.2",
    "vite": "^5.3.1"
  }
}
```

## TAILWIND_CONFIG_CRITICAL
```typescript
// tailwind.config.ts - EXACT_COPY_REQUIRED
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        background: '#0a0a0f',
        elevated: '#13131a',
        primary: '#6366f1',
        secondary: '#8b5cf6',
        accent: '#14b8a6',
        text: {
          DEFAULT: '#f8fafc',
          muted: '#94a3b8',
        },
        border: '#1e293b',
        destructive: '#ef4444',
        muted: {
          DEFAULT: '#1e293b',
          foreground: '#64748b',
        },
      },
      animation: {
        'glow': 'glow 2s ease-in-out infinite',
      },
      keyframes: {
        glow: {
          '0%, 100%': { boxShadow: '0 0 20px 10px rgba(99, 102, 241, 0.3)' },
          '50%': { boxShadow: '0 0 30px 15px rgba(99, 102, 241, 0.5)' },
        }
      }
    },
  },
  plugins: [],
}
```

## LAYOUT_DIMENSIONS_EXACT
```
SIDEBAR_WIDTH: 256px (w-64)
SIDEBAR_TOGGLE_POSITION: top-20 (80px from top)
HEADER_HEIGHT: 64px (h-16)
RIGHT_PANEL_WIDTH: 384px (w-96)
SLIDE_CANVAS_MAX_WIDTH: 1024px (max-w-4xl)
SLIDE_CANVAS_ASPECT_RATIO: 16/10
GENERATE_BUTTON_POSITION: bottom-8 left-1/2 -translate-x-1/2
GENERATE_DIALOG_MIN_WIDTH: 500px
```

## COMPONENT_1_SIDEBAR
```tsx
// EXACT_IMPLEMENTATION - Sidebar.tsx
import React from 'react'
import { ChevronLeft, ChevronRight } from '@mui/icons-material'
import { cn } from '@/lib/utils'

// CRITICAL: Toggle button at top-20 NOT top-4
// CRITICAL: Sidebar bg-elevated with border-r border-border
// CRITICAL: transition-all duration-300 for smooth animation
// MOCK_DATA: 8 items ["Pitch meeting 24th", "Client Demo", "Hackathon Deck", "AI brainstorming", "Financial Meeting", "Board meeting deck", "School project", "History presentation"]

const Sidebar = ({ isOpen, onToggle, pastChats, selectedChatId, onChatSelect }) => (
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
```

## COMPONENT_2_GENERATE_BUTTON
```tsx
// CRITICAL_FEATURES:
// 1. ALWAYS_CENTERED: left-1/2 -translate-x-1/2 NO ml-32 adjustment
// 2. DYNAMIC_BUTTON: Cancel when empty, Send with icon when text exists
// 3. CLICK_OUTSIDE_CLOSE: useEffect with mousedown listener
// 4. FORMAT_SLIDER: NOT separate buttons, single container with selected state

import React, { useState, useRef, useEffect } from 'react'
import { Send } from '@mui/icons-material'
import { motion, AnimatePresence } from 'framer-motion'

const GenerateButton = ({ onGenerate, isGenerating, isSidebarOpen }) => {
  const [prompt, setPrompt] = useState('')
  const [isExpanded, setIsExpanded] = useState(false)
  const [selectedFormat, setSelectedFormat] = useState<'PPTX' | 'PDF' | 'TeX'>('PPTX')
  const dialogRef = useRef<HTMLDivElement>(null)

  // CRITICAL: Click outside handler
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dialogRef.current && !dialogRef.current.contains(event.target as Node)) {
        setIsExpanded(false)
        setPrompt('')
      }
    }
    if (isExpanded) {
      document.addEventListener('mousedown', handleClickOutside)
      return () => document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isExpanded])

  return (
    <div className="fixed bottom-8 left-1/2 -translate-x-1/2 transition-all duration-300 z-10">
      <AnimatePresence>
        {!isExpanded ? (
          <motion.button
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            onClick={() => setIsExpanded(true)}
            className="px-8 py-4 bg-primary text-white rounded-xl font-semibold hover:bg-primary/90 shadow-lg hover:shadow-xl"
          >
            Generate...
          </motion.button>
        ) : (
          <motion.div
            ref={dialogRef}
            initial={{ opacity: 0, scale: 0.9, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            className="relative"
          >
            <div className="bg-elevated/95 backdrop-blur-xl border border-primary/30 rounded-2xl p-6 shadow-2xl min-w-[500px]">
              <textarea
                autoFocus
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                placeholder="Describe your presentation..."
                className="w-full h-24 bg-background/50 border border-border rounded-lg px-4 py-3 text-text resize-none focus:outline-none focus:border-primary/50"
              />
              <div className="flex items-center justify-between mt-4">
                <div className="flex items-center gap-2 bg-background/50 rounded-full p-1">
                  {(['PPTX', 'PDF', 'TeX'] as const).map(format => (
                    <button
                      key={format}
                      onClick={() => setSelectedFormat(format)}
                      className={cn(
                        'px-4 py-1.5 rounded-full text-sm font-medium transition-all duration-200',
                        selectedFormat === format
                          ? 'bg-primary text-white shadow-lg'
                          : 'text-text-muted hover:text-text'
                      )}
                    >
                      {format}
                    </button>
                  ))}
                </div>
                {prompt.trim() ? (
                  <button className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90">
                    <Send className="w-4 h-4" />
                    Send
                  </button>
                ) : (
                  <button onClick={() => setIsExpanded(false)} className="text-text-muted hover:text-text">
                    Cancel
                  </button>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
```

## COMPONENT_3_SLIDE_CONTENT_PANEL
```tsx
// CRITICAL_LAYOUT:
// 1. HEADER: Slide title as h3 NOT input, NO duplicate counter
// 2. BOTTOM_SECTION: textarea with rows={2} pb-10 for height
// 3. BUTTONS_POSITION: bottom-2 NOT center
// 4. QUICK_ACTIONS: Above input ["Add Detail", "Simplify", "Add Examples", "Change tone"]

const SlideContentPanel = ({ slide, currentSlideNumber, totalSlides, className }) => {
  const [modificationPrompt, setModificationPrompt] = useState('')

  return (
    <div className={cn('bg-elevated border-l border-border flex flex-col h-full', className)}>
      <div className="p-4 border-b border-border">
        <h3 className="text-lg font-medium text-text">{slide?.title || 'Slide Title'}</h3>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        <div className="bg-background/50 border border-border rounded-lg p-4 mb-4">
          <div className="text-sm text-text-muted mb-2">{slide?.content || 'This slide provides...'}</div>
        </div>
        <div className="bg-background/50 border border-border rounded-lg p-4 text-sm text-text/80">
          Fusce nec rutrum velit...
        </div>
        <div className="flex justify-end mt-6 mb-4 px-2">
          <button className="flex items-center gap-1 text-xs text-text-muted hover:text-text">
            <AutoAwesome className="w-3 h-3" />
            <span>AI Overview</span>
          </button>
        </div>
      </div>

      <div className="p-4 border-t border-border">
        <div className="flex flex-wrap gap-2 mb-3">
          {['Add Detail', 'Simplify', 'Add Examples', 'Change tone'].map(action => (
            <button key={action} className="px-3 py-1 bg-primary/10 text-xs text-text/70 rounded-full hover:bg-primary/20">
              {action}
            </button>
          ))}
        </div>
        <div className="relative">
          <textarea
            value={modificationPrompt}
            onChange={(e) => setModificationPrompt(e.target.value)}
            placeholder="Describe how you want to modify this slide..."
            className="w-full bg-background/50 border border-border rounded-lg pl-4 pr-20 pt-3 pb-10 text-sm text-text resize-none"
            rows={2}
          />
          <div className="absolute right-2 bottom-2 flex items-center gap-2">
            <button className="p-1.5 hover:bg-primary/10 rounded"><AttachFile className="w-4 h-4 text-text-muted" /></button>
            <button className="p-1.5 bg-primary/20 hover:bg-primary/30 rounded"><Send className="w-4 h-4 text-primary" /></button>
          </div>
        </div>
      </div>
    </div>
  )
}
```

## COMPONENT_4_SLIDE_CANVAS
```tsx
// GRADIENT: bg-gradient-to-b from-gray-700 to-gray-800
// ASPECT_RATIO: aspect-[16/10] CRITICAL
// SHADOW: shadow-2xl

const SlideCanvas = ({ slide, className }) => (
  <div className={cn(
    'bg-gradient-to-b from-gray-700 to-gray-800 rounded-lg shadow-2xl aspect-[16/10] flex items-center justify-center',
    className
  )}>
    {slide ? (
      <div className="p-8 w-full h-full flex flex-col">
        <h2 className="text-3xl font-bold text-white mb-4">{slide.title}</h2>
        <div className="text-lg text-gray-200 flex-1">{slide.content}</div>
      </div>
    ) : (
      <div className="text-gray-400 text-center">
        <p className="text-xl">No slide selected</p>
        <p className="text-sm mt-2">Generate or select a presentation to begin</p>
      </div>
    )}
  </div>
)
```

## APP_LAYOUT_STRUCTURE
```tsx
// CRITICAL_LAYOUT:
// 1. Main content ml-64 when sidebar open, ml-0 when closed
// 2. Header fixed height h-16
// 3. Content area flex-1 flex overflow-hidden
// 4. SlideCanvas centered with max-w-4xl
// 5. SlideContentPanel fixed w-96

<div className="h-screen flex flex-col bg-background overflow-hidden">
  <Sidebar isOpen={isSidebarOpen} ... />

  <div className={cn('flex-1 flex flex-col transition-all duration-300',
    isSidebarOpen ? 'ml-64' : 'ml-0')}>

    <Header currentSlide={1} totalSlides={10} ... />

    <div className="flex-1 flex overflow-hidden">
      <div className="flex-1 p-8 flex items-center justify-center">
        <SlideCanvas slide={mockSlide} className="max-w-4xl w-full" />
      </div>
      <SlideContentPanel ... className="w-96 h-full" />
    </div>
  </div>

  <GenerateButton ... isSidebarOpen={isSidebarOpen} />
</div>
```

## CRITICAL_PITFALLS_AVOID

### PITFALL_1_SIDEBAR_TOGGLE_POSITION
WRONG: top-4
CORRECT: top-20
REASON: Prevents overlap with header content

### PITFALL_2_GENERATE_BUTTON_CENTERING
WRONG: Using ml-32 adjustment when sidebar open
CORRECT: Always left-1/2 -translate-x-1/2
REASON: Button must remain centered on viewport

### PITFALL_3_FORMAT_SELECTOR
WRONG: Separate buttons for PPTX/PDF/TeX
CORRECT: Single container with sliding selection state
REASON: Visual cohesion and interaction pattern

### PITFALL_4_RIGHT_PANEL_INPUT
WRONG: input type="text" with centered buttons
CORRECT: textarea rows={2} with pb-10 and bottom-2 buttons
REASON: Prevents placeholder text cutoff

### PITFALL_5_SLIDE_TITLE_EDITABILITY
WRONG: input field in right panel header
CORRECT: h3 heading element
REASON: Not user-editable, display only

## CSS_UTILITIES_REQUIRED
```typescript
// lib/utils.ts
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

## INDEX_CSS_BASE
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  html, body {
    @apply bg-background text-text;
    height: 100%;
    margin: 0;
    padding: 0;
  }
  #root { height: 100%; }
}

@layer components {
  .glass-effect { @apply backdrop-blur-lg bg-elevated/50 border border-border; }
  .glow-effect { box-shadow: 0 0 20px 10px rgba(99, 102, 241, 0.2); }
  .slide-preview { @apply bg-gradient-to-b from-gray-700 to-gray-800 rounded-lg; }
}
```

## MOCK_DATA_STRUCTURE
```typescript
interface Slide {
  id: string
  title: string
  content: string
  layout?: 'title' | 'content' | 'two-column' | 'image'
  notes?: string
}

interface PastChat {
  id: string
  title: string
  timestamp: Date
  presentationId?: string
}

const mockPastChats: PastChat[] = [
  { id: '1', title: 'Pitch meeting 24th', timestamp: new Date() },
  { id: '2', title: 'Client Demo', timestamp: new Date() },
  { id: '3', title: 'Hackathon Deck', timestamp: new Date() },
  { id: '4', title: 'AI brainstorming', timestamp: new Date() },
  { id: '5', title: 'Financial Meeting', timestamp: new Date() },
  { id: '6', title: 'Board meeting deck', timestamp: new Date() },
  { id: '7', title: 'School project', timestamp: new Date() },
  { id: '8', title: 'History presentation', timestamp: new Date() }
]

const mockSlide: Slide = {
  id: '1',
  title: 'Introduction to AI',
  content: 'This slide provides an overview of artificial intelligence and its applications in modern technology.'
}
```

## VISUAL_VERIFICATION_CHECKPOINTS
1. Background=#0a0a0f everywhere except elevated surfaces
2. Sidebar slide animation smooth 300ms
3. Generate button perfectly centered horizontally
4. Format selector shows selected state with bg-primary
5. Slide canvas maintains 16:10 aspect ratio
6. Right panel textarea allows 2 lines minimum height
7. All borders use #1e293b color
8. Header items properly spaced with slide navigation centered

## BUILD_SEQUENCE_CRITICAL
1. Setup Vite+React+TS project
2. Install ALL dependencies EXACT versions
3. Configure Tailwind with EXACT color palette
4. Create folder structure BEFORE components
5. Implement utils.ts first
6. Build components in order: Sidebar->Header->SlideCanvas->SlideContentPanel->GenerateButton->SlideNavigator
7. Assemble in App.tsx with exact layout structure
8. Verify with dev server at 1440x1024 viewport

## ANIMATIONS_TRANSITIONS
- Sidebar: transition-all duration-300
- Buttons: hover transitions with /10 /20 /30 opacity variants
- Generate dialog: framer-motion scale+opacity+y
- All hover states: transition-colors
- No spring animations, only CSS transitions except Generate dialog

## FINAL_VALIDATION
Component count: 6 main + App.tsx
Color usage: background/elevated/primary/text/text-muted/border ONLY
MUI icons: ChevronLeft/Right, Send, AttachFile, AutoAwesome, ContentCopy
State management: Local useState only, no context/redux
Mock data: Always 8 past chats, 1 slide, 10 total slides

END_SPEC_V1