# COMPLETE_MISSING_CRITICAL_DETAILS_V1

## VITE_CONFIG_EXACT
```typescript
// vite.config.ts - MUST HAVE PATH ALIAS
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})
```

## TSCONFIG_PATHS_CRITICAL
```json
// tsconfig.json - PATH MAPPING REQUIRED
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
    // other options...
  }
}
```

## HTML_TEMPLATE_EXACT
```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>AI Slides - Presentation Generator</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

## MAIN_TSX_ENTRY
```tsx
// src/main.tsx - EXACT STRUCTURE
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

## HEADER_COMPONENT_COMPLETE
```tsx
// Header.tsx - MISSING FROM ORIGINAL SPEC
import React from 'react'
import { cn } from '@/lib/utils'
import { SlideNavigator } from '../presentation/SlideNavigator'

interface HeaderProps {
  currentSlide: number
  totalSlides: number
  onNavigate: (slideNumber: number) => void
  presentationTitle?: string
}

export const Header: React.FC<HeaderProps> = ({
  currentSlide,
  totalSlides,
  onNavigate,
  presentationTitle = 'Slide Title'
}) => {
  return (
    <header className="h-16 bg-background border-b border-border flex items-center justify-between px-6">
      <div className="flex items-center gap-8 flex-1">
        <input
          type="text"
          value={presentationTitle}
          className="bg-transparent text-text text-lg font-medium focus:outline-none"
          placeholder="Presentation Title"
        />
      </div>

      <div className="flex items-center gap-6">
        <SlideNavigator
          currentSlide={currentSlide}
          totalSlides={totalSlides}
          onNavigate={onNavigate}
        />

        <div className="flex items-center gap-2 text-sm">
          <button className={cn(
            'px-3 py-1.5 rounded-lg transition-colors',
            'text-text-muted hover:text-text hover:bg-primary/10'
          )}>
            Old Draft
          </button>
          <button className={cn(
            'px-3 py-1.5 rounded-lg transition-colors',
            'text-text-muted hover:text-text hover:bg-primary/10'
          )}>
            Simplify
          </button>
          <button className={cn(
            'px-3 py-1.5 rounded-lg transition-colors',
            'text-text-muted hover:text-text hover:bg-primary/10'
          )}>
            Full Example
          </button>
          <button className={cn(
            'px-3 py-1.5 rounded-lg transition-colors',
            'text-text-muted hover:text-text hover:bg-primary/10'
          )}>
            Fine-grain
          </button>
        </div>
      </div>
    </header>
  )
}
```

## SLIDE_NAVIGATOR_COMPLETE
```tsx
// SlideNavigator.tsx - MISSING COMPONENT
import React from 'react'
import { ChevronLeft, ChevronRight } from '@mui/icons-material'
import { cn } from '@/lib/utils'

interface SlideNavigatorProps {
  currentSlide: number
  totalSlides: number
  onNavigate: (slideNumber: number) => void
}

export const SlideNavigator: React.FC<SlideNavigatorProps> = ({
  currentSlide,
  totalSlides,
  onNavigate
}) => {
  const handlePrevious = () => {
    if (currentSlide > 1) {
      onNavigate(currentSlide - 1)
    }
  }

  const handleNext = () => {
    if (currentSlide < totalSlides) {
      onNavigate(currentSlide + 1)
    }
  }

  return (
    <div className="flex items-center gap-4">
      <button
        onClick={handlePrevious}
        disabled={currentSlide === 1}
        className={cn(
          'p-2 rounded-lg transition-colors',
          currentSlide === 1
            ? 'text-text-muted cursor-not-allowed opacity-50'
            : 'text-text hover:bg-primary/10'
        )}
      >
        <ChevronLeft className="w-5 h-5" />
      </button>

      <div className="text-text">
        <span className="font-medium">{currentSlide}</span>
        <span className="text-text-muted mx-2">/</span>
        <span className="text-text-muted">{totalSlides}</span>
      </div>

      <button
        onClick={handleNext}
        disabled={currentSlide === totalSlides}
        className={cn(
          'p-2 rounded-lg transition-colors',
          currentSlide === totalSlides
            ? 'text-text-muted cursor-not-allowed opacity-50'
            : 'text-text hover:bg-primary/10'
        )}
      >
        <ChevronRight className="w-5 h-5" />
      </button>
    </div>
  )
}
```

## APP_COMPONENT_COMPLETE_WITH_STATE
```tsx
// App.tsx - COMPLETE WITH ALL STATE MANAGEMENT
import React, { useState } from 'react'
import { Sidebar } from './components/layout/Sidebar'
import { Header } from './components/layout/Header'
import { SlideCanvas } from './components/presentation/SlideCanvas'
import { SlideContentPanel } from './components/presentation/SlideContentPanel'
import { GenerateButton } from './components/presentation/GenerateButton'
import { cn } from './lib/utils'
import { PastChat, Slide } from './types/presentation'

const mockPastChats: PastChat[] = [
  { id: '1', title: 'Pitch meeting 24th', timestamp: new Date() },
  { id: '2', title: 'Client Demo', timestamp: new Date() },
  { id: '3', title: 'Hackathon Deck', timestamp: new Date() },
  { id: '4', title: 'AI brainstorming', timestamp: new Date() },
  { id: '5', title: 'Financial Meeting', timestamp: new Date() },
  { id: '6', title: 'Board meeting deck', timestamp: new Date() },
  { id: '7', title: 'School project', timestamp: new Date() },
  { id: '8', title: 'History presentation', timestamp: new Date() },
]

const mockSlide: Slide = {
  id: '1',
  title: 'Introduction to AI',
  content: `This slide provides an overview of artificial intelligence and its applications in modern technology.

Fusce nec rutrum velit. In vitae ex cursus, condimentum mi at, aliquet lorem. Integer ornare tellus augue, at lacinia elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer ornare tellus augue, in mauris non faucibus volutpat et velit ligula. Donec feugiat quam vel, aute mauris lacinia aliquam ornare. Sed finibus mauris non felis ultricies tincidunt. Fusce sem tellus, fringilla eget sapien sed, ornare maximus ligula.`
}

function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)
  const [selectedChatId, setSelectedChatId] = useState<string>()
  const [currentSlide, setCurrentSlide] = useState(1)
  const [isGenerating, setIsGenerating] = useState(false)
  const totalSlides = 10

  const handleGenerate = (prompt: string, format: 'PPTX' | 'PDF' | 'TeX') => {
    console.log('Generating presentation:', { prompt, format })
    setIsGenerating(true)
    setTimeout(() => {
      setIsGenerating(false)
    }, 3000)
  }

  return (
    <div className="h-screen flex flex-col bg-background overflow-hidden">
      <Sidebar
        isOpen={isSidebarOpen}
        onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
        pastChats={mockPastChats}
        selectedChatId={selectedChatId}
        onChatSelect={setSelectedChatId}
      />

      <div
        className={cn(
          'flex-1 flex flex-col transition-all duration-300',
          isSidebarOpen ? 'ml-64' : 'ml-0'
        )}
      >
        <Header
          currentSlide={currentSlide}
          totalSlides={totalSlides}
          onNavigate={setCurrentSlide}
          presentationTitle="Slide Title"
        />

        <div className="flex-1 flex overflow-hidden">
          <div className="flex-1 p-8 flex items-center justify-center">
            <SlideCanvas
              slide={mockSlide}
              className="max-w-4xl w-full"
            />
          </div>

          <SlideContentPanel
            slide={mockSlide}
            currentSlideNumber={currentSlide}
            totalSlides={totalSlides}
            className="w-96 h-full"
          />
        </div>
      </div>

      <GenerateButton
        onGenerate={handleGenerate}
        isGenerating={isGenerating}
        isSidebarOpen={isSidebarOpen}
      />
    </div>
  )
}

export default App
```

## ANIMATION_SPECIFICATIONS_EXACT
```css
/* All animation timings and easing functions */
SIDEBAR_SLIDE: transition-all duration-300 ease-in-out
BUTTON_HOVER: transition-colors duration-200 ease-in-out
GENERATE_EXPAND: scale(0.9->1) opacity(0->1) y(20px->0) duration-200 ease-out
GENERATE_COLLAPSE: scale(1->0.9) opacity(1->0) y(0->20px) duration-150 ease-in
FORMAT_SELECTOR: transition-all duration-200 ease-in-out
FOCUS_TRANSITIONS: transition-colors duration-150 ease-in-out
SHADOW_TRANSITIONS: transition-shadow duration-200 ease-in-out
GLOW_ANIMATION: animation-duration-2000ms ease-in-out infinite
```

## POSTCSS_CONFIG_EXACT
```javascript
// postcss.config.js
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

## IMPORT_STATEMENTS_ORDER
```typescript
// ALWAYS THIS ORDER:
// 1. React imports
import React, { useState, useRef, useEffect } from 'react'
// 2. External libraries
import { motion, AnimatePresence } from 'framer-motion'
// 3. MUI icons
import { ChevronLeft, ChevronRight, Send, AttachFile, AutoAwesome } from '@mui/icons-material'
// 4. Local utilities
import { cn } from '@/lib/utils'
// 5. Types
import { Slide, PastChat } from '@/types/presentation'
// 6. Components
import { ComponentName } from '@/components/...'
```

## EDGE_CASES_HANDLING

### EMPTY_STATES
- No slide selected: Show "No slide selected" message
- Empty past chats: Still show header "Past Chats"
- No presentation title: Placeholder "Presentation Title"
- Empty modification prompt: Placeholder visible

### OVERFLOW_HANDLING
- Past chats list: overflow-y-auto
- Slide content: Text wraps, no horizontal scroll
- Right panel content: overflow-y-auto on main area
- Long titles: truncate class on chat items

### DISABLED_STATES
- Previous button disabled when currentSlide === 1
- Next button disabled when currentSlide === totalSlides
- Generate button disabled during isGenerating
- All inputs readonly when no slide selected

### RESPONSIVE_BREAKPOINTS
```css
/* ONLY 1440px WIDTH TESTED - NO RESPONSIVE DESIGN */
/* DO NOT ADD RESPONSIVE BREAKPOINTS */
/* FIXED WIDTH COMPONENTS ONLY */
```

## Z_INDEX_HIERARCHY
```css
z-10: Generate button
z-20: Sidebar
z-30: Sidebar toggle button
z-40: Modals/Dialogs (if any)
```

## HOVER_STATE_MAP
```
ELEMENT                    | HOVER_CLASS
---------------------------|---------------------------
Sidebar items              | hover:bg-primary/10
Sidebar toggle             | hover:bg-primary/10
Header buttons             | hover:bg-primary/10 hover:text-text
Generate button            | hover:bg-primary/90 hover:shadow-xl
Quick action chips         | hover:bg-primary/20
Format selector inactive   | hover:text-text
AI Overview button         | hover:text-text
Attachment button          | hover:bg-primary/10
Send button                | hover:bg-primary/30
```

## FOCUS_OUTLINE_REMOVAL
```css
/* ALL INPUTS AND BUTTONS */
focus:outline-none
/* REPLACED WITH */
focus:border-primary or focus:border-primary/50
```

## FONT_WEIGHTS_MAP
```
font-normal: 400 (default text)
font-medium: 500 (titles, buttons)
font-semibold: 600 (headings)
font-bold: 700 (slide canvas title only)
```

## OPACITY_VARIANTS_USED
```
/10: 10% opacity (hover backgrounds)
/20: 20% opacity (active states)
/30: 30% opacity (stronger active)
/50: 50% opacity (placeholders, semi-transparent)
/70: 70% opacity (quick action text)
/80: 80% opacity (content text variant)
/90: 90% opacity (hover on solid colors)
/95: 95% opacity (dialog backgrounds)
```

## BORDER_RADIUS_VALUES
```
rounded: 4px (default, rarely used)
rounded-lg: 8px (most components)
rounded-xl: 12px (generate button)
rounded-2xl: 16px (generate dialog)
rounded-full: 9999px (chips, format selector)
```

## MISSING_MUI_ICON_IMPORT
```typescript
// COMPLETE LIST OF MUI ICONS USED:
import {
  ChevronLeft,      // Sidebar toggle, slide navigation
  ChevronRight,     // Sidebar toggle, slide navigation
  Send,             // Right panel send, generate dialog send
  AttachFile,       // Right panel attachment
  AutoAwesome,      // AI Overview button
  ContentCopy       // Not used in final version (removed)
} from '@mui/icons-material'
```

## NPM_SCRIPTS_COMPLETE
```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "lint": "eslint .",
    "preview": "vite preview"
  }
}
```

## BROWSER_CONSOLE_WARNINGS_EXPECTED
```
Warning: You provided a `value` prop without `onChange` handler
// IGNORE - This is for display-only fields
```

## STATE_INITIALIZATION_VALUES
```typescript
const [isSidebarOpen, setIsSidebarOpen] = useState(true) // START OPEN
const [selectedChatId, setSelectedChatId] = useState<string>() // UNDEFINED
const [currentSlide, setCurrentSlide] = useState(1) // START AT 1
const [isGenerating, setIsGenerating] = useState(false) // START FALSE
const [prompt, setPrompt] = useState('') // EMPTY STRING
const [modificationPrompt, setModificationPrompt] = useState('') // EMPTY
const [selectedFormat, setSelectedFormat] = useState<'PPTX'|'PDF'|'TeX'>('PPTX') // DEFAULT PPTX
const [hovering, setHovering] = useState(false) // FALSE
const [isExpanded, setIsExpanded] = useState(false) // START COLLAPSED
```

## TESTING_VIEWPORT_CRITICAL
```
WIDTH: 1440px EXACT
HEIGHT: 1024px MINIMUM
ZOOM: 100%
BROWSER: Chrome/Edge/Firefox modern
DARK_MODE: System preference ignored, always dark
```

## FILE_NAMING_CONVENTIONS
```
Components: PascalCase.tsx
Utilities: camelCase.ts
Types: camelCase.ts
Styles: camelCase.css
Config: camelCase.config.ts/js
```

## BUILD_VERIFICATION_CHECKLIST
1. npm create vite@latest frontend -- --template react-ts
2. cd frontend && npm install [all deps exact versions]
3. Replace all config files before npm run dev
4. Create folder structure first
5. Copy utils.ts exactly
6. Build components in dependency order
7. Test at 1440x1024 viewport
8. Verify no console errors except value/onChange warning
9. Test all interactions work
10. Verify colors match exactly in devtools

## COMMON_MISTAKES_TO_AVOID
1. DO NOT use responsive breakpoints
2. DO NOT add extra animations
3. DO NOT change color values
4. DO NOT add backdrop-blur without browser prefix
5. DO NOT forget path alias @ configuration
6. DO NOT add extra npm packages
7. DO NOT change aspect ratio from 16/10
8. DO NOT position buttons center in textarea
9. DO NOT make right panel title editable
10. DO NOT add loading spinners

END_MISSING_DETAILS_V1