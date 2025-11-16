# Frontend UI Implementation Plan - AI PPT Maker

## Executive Summary
Build React/TypeScript frontend for AI PPT maker with ChatGPT-like interface, PPTX/PDF viewer, and slide-level editing capabilities. Focus on MVP with minimal, functional code.

---

## Phase 1: Project Setup & Foundation
**Goal:** Initialize React project with required stack

### Tasks
- Init Vite + React + TypeScript project in `/frontend` directory
- Install core deps: TailwindCSS, MUI, TanStack Router, Axios
- Install viewer deps: react-pdf (PDF), pptx-preview (PPTX native rendering)
- Setup folder structure: `/components`, `/services`, `/types`, `/hooks`, `/store`
- Configure Tailwind with dark theme colors from README
- Setup API client service with base URL config
- Create TypeScript types matching backend schemas

### Key Files
- `frontend/vite.config.ts` - Vite configuration with proxy to backend
- `frontend/tailwind.config.js` - Dark theme colors from README
- `frontend/src/services/api.ts` - Axios client with interceptors
- `frontend/src/types/index.ts` - API response/request types

---

## Phase 2: Core Layout & Routing
**Goal:** Three-panel layout with responsive design

### Layout Structure
```
+----------+------------------+-----------+
| Sidebar  |   Main Content   | Inspector |
| (300px)  |    (flex-1)      |  (350px)  |
+----------+------------------+-----------+
```

### Components
- `AppLayout.tsx` - Main container with 3-panel grid
- `Sidebar.tsx` - Left panel with chat history
- `MainView.tsx` - Center area container
- `SlideInspector.tsx` - Right panel (hidden initially)

### Features
- Collapsible sidebar on mobile and pc (hide sidebar and show sidebar button)
- Inspector panel slides in when presentation generated
- Dark background (#0a0a0f) with border colors (#1e293b)

---

## Phase 3: Sidebar - Chat Management
**Goal:** ChatGPT-style presentation history

### Components
- `ChatList.tsx` - List of past presentations
- `ChatItem.tsx` - Individual chat/presentation card
- `NewChatButton.tsx` - Prominent "New Presentation" button

### API Integration
- GET `/api/v1/presentations/` - Fetch presentation list
- DELETE `/api/v1/presentations/{id}` - Delete presentation
- Implement pagination with infinite scroll

### UI Features
- Show presentation title (truncated main_topic)
- Timestamp display
- Hover actions (delete, rename)
- Active state highlighting
- Search/filter presentations

---

## Phase 4: Main Content - Prompt & Viewer
**Goal:** Prompt input and presentation display

### Components
- `PromptInput.tsx` - Main textarea with send button
- `PresentationViewer.tsx` - Container for viewer selection
- `PDFViewer.tsx` - Embed PDF using react-pdf library
- `PPTXViewer.tsx` - Native PPTX viewer using pptx-preview (no image conversion)
- `FormatSelector.tsx` - Toggle between PDF/PPTX output

### States
1. **Empty State** - Show prompt input centered
2. **Loading State** - Generation progress with skeleton
3. **View State** - Display generated presentation

### API Integration
- POST `/api/v1/presentations/` - Create presentation
- Serve files from `/generated_files/{type}/{uuid}.{ext}`

### UI Features
- Auto-expanding textarea
- Format selection chips (PDF/PPTX)
- Download button for generated files
- Slide navigation controls
- Zoom controls for viewer

### Viewer Implementation Details
**PDF Viewer (react-pdf):**
- Lightweight (~200KB bundle)
- Page-by-page navigation
- Zoom in/out controls
- Download PDF button

**PPTX Viewer (pptx-preview):**
- Native PPTX parsing in browser
- Client-side rendering without conversion
- Loads file as ArrayBuffer from backend
- Slide navigation with thumbnails
- Note: Bundle size ~1.76MB (acceptable for MVP)

---

## Phase 5: Slide Inspector - Iterative Editing
**Goal:** Per-slide editing interface

### Components
- `SlideEditor.tsx` - Main editing interface
- `SlidePrompt.tsx` - Textarea for slide modifications
- `SlideSelector.tsx` - Current slide indicator/selector
- `SlideContext.tsx` - Show adjacent slides for context

### Features
- Auto-detect current slide from viewer
- Show slide number and title
- Edit prompt with suggestions
- Show before/after slides as context
- Apply changes with loading state

### API Integration
- PUT `/api/v1/presentations/{id}` - Update slide
- Auto-refresh viewer after update

---

## Phase 6: State Management & Real-time Updates
**Goal:** Smooth data flow and UI updates

### Implementation
- Use React Context for global state
- Store current presentation, selected slide, loading states
- Implement optimistic updates for better UX
- Cache presentations in localStorage

### Key States
```typescript
interface AppState {
  presentations: Presentation[]
  currentPresentation: Presentation | null
  selectedSlide: number
  isGenerating: boolean
  isEditing: boolean
  viewerType: 'pdf' | 'pptx'
}
```

---

## Phase 7: Polish & Optimization
**Goal:** Production-ready UI

### Tasks
- Loading skeletons for all async operations
- Error boundaries and toast notifications
- Keyboard shortcuts (Cmd+N new, Cmd+Enter send)
- Mobile responsive design
- Performance optimization (lazy loading, memoization)
- Accessibility (ARIA labels, keyboard navigation)

### UI Enhancements
- Smooth animations with Framer Motion
- Glass-morphism effects for panels
- Gradient accents on buttons
- Tooltips for all actions

---

## Technical Specifications

### API Service Pattern
```typescript
class APIService {
  async createPresentation(topic: string, fileType: 'pdf' | 'pptx')
  async getPresentation(id: string)
  async updateSlide(id: string, slideNumber: number, content: string)
  async deletePresentation(id: string)
  async listPresentations(skip?: number, limit?: number)
}
```

### Component Architecture
- Functional components with hooks
- Custom hooks for data fetching
- Proper error handling with fallbacks
- TypeScript strict mode

### Styling Approach
- Tailwind utility classes
- CSS modules for complex components
- MUI components styled with theme
- No inline styles

---

## File Structure
```
frontend/
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AppLayout.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── SlideInspector.tsx
│   │   ├── chat/
│   │   │   ├── ChatList.tsx
│   │   │   └── ChatItem.tsx
│   │   ├── viewer/
│   │   │   ├── PresentationViewer.tsx
│   │   │   ├── PDFViewer.tsx
│   │   │   └── PPTXViewer.tsx
│   │   └── editor/
│   │       ├── SlideEditor.tsx
│   │       └── PromptInput.tsx
│   ├── services/
│   │   └── api.ts
│   ├── hooks/
│   │   ├── usePresentation.ts
│   │   └── useSlideEditor.ts
│   ├── types/
│   │   └── index.ts
│   ├── store/
│   │   └── AppContext.tsx
│   └── App.tsx
├── package.json
├── vite.config.ts
└── tailwind.config.js
```

---

## Development Guidelines

### Code Quality
- No console.logs in production
- No hardcoded values
- Environment variables for API URL
- Proper TypeScript types (no `any`)
- Component files < 200 lines

### MVP Focus
- Skip authentication/login
- Skip advanced features (templates, themes)
- Skip analytics/telemetry
- Focus on core functionality
- Minimal dependencies

### Performance Targets
- Initial load < 3s
- API response handling < 100ms
- Smooth 60fps animations
- Bundle size < 2MB (larger due to pptx-preview, but acceptable for rich PPTX viewing)

---

## Implementation Checklist

**Developer Instructions:** Mark items with ✅ as you complete each phase. Update status after implementing each component.

### Phase 1: Project Setup
- [✅] Initialize Vite React TypeScript project
- [✅] Install and configure TailwindCSS
- [✅] Install MUI and other dependencies
- [✅] Setup project structure
- [✅] Configure API client
- [✅] Create TypeScript types

### Phase 2: Core Layout
- [✅] Implement AppLayout component
- [✅] Create Sidebar component
- [✅] Create MainView component
- [✅] Create SlideInspector component
- [✅] Add responsive design

### Phase 3: Sidebar Features
- [ ] Implement ChatList with API integration
- [ ] Create ChatItem component
- [ ] Add NewChatButton
- [ ] Implement delete functionality
- [ ] Add search/filter

### Phase 4: Main Content
- [ ] Create PromptInput component
- [ ] Implement PresentationViewer
- [ ] Add PDF viewer
- [ ] Add PPTX viewer
- [ ] Create FormatSelector
- [ ] Add download functionality

### Phase 5: Slide Inspector
- [ ] Implement SlideEditor
- [ ] Create SlidePrompt input
- [ ] Add SlideSelector
- [ ] Show slide context
- [ ] Integrate update API

### Phase 6: State Management
- [ ] Setup React Context
- [ ] Implement global state
- [ ] Add localStorage caching
- [ ] Implement optimistic updates

### Phase 7: Polish
- [ ] Add loading skeletons
- [ ] Implement error handling
- [ ] Add keyboard shortcuts
- [ ] Optimize performance
- [ ] Test mobile responsiveness
- [ ] Add accessibility features

---

## Testing Checklist
- [ ] Create new presentation
- [ ] View PDF output
- [ ] View PPTX output
- [ ] Edit individual slide
- [ ] Delete presentation
- [ ] Navigate presentation history
- [ ] Test on mobile devices
- [ ] Test error states
- [ ] Test loading states

---

## Notes for Developers
1. Start with Phase 1-2 to get basic structure
2. Phases 3-5 can be developed in parallel by different devs
3. Use mock data initially, integrate API gradually
4. Test each component in isolation before integration
5. Keep components pure and testable
6. Document any deviations from this plan
7. **PPTX Viewer Note:** Using `pptx-preview` for native PPTX rendering (no image conversion). This adds ~1.76MB to bundle but provides true client-side PPTX viewing as required

---

**End of Plan Document**

*This plan prioritizes speed of development while maintaining code quality. Focus on shipping working features over perfect code.*