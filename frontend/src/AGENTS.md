# FRONTEND SOURCE

React 18 + Vite + TailwindCSS presentation generator UI.

## STRUCTURE

```
src/
├── components/
│   ├── presentation/   # GenerateButton, SlideCanvas, SlideNavigator
│   ├── layout/         # Sidebar, Header, MainLayout, HamburgerMenu
│   ├── rag/            # DocumentUpload, DocumentUploadInline, DocumentAttachSelector, DocumentProgressCard
│   ├── viewer/         # DocumentViewer, SimplifiedDocumentViewer (PDF display)
│   ├── editor/         # SlideEditor
│   ├── ui/             # Primitives: button, card, select, progress, badge, switch, icon, separator,
│   │                   #   LoadingOverlay, ParticleBackground, FirstTimeTooltip
│   └── onboarding/     # OnboardingStep
├── pages/              # Workspace, DocumentLibrary, HomePage, NotFound
├── services/
│   ├── api.ts          # presentationApi, ragApi (335 lines)
│   └── sse.ts          # Server-sent events for document progress
├── types/              # TypeScript interfaces (api.ts, index.ts, presentation.ts)
├── utils/              # errorHandler.ts, fileUrls.ts
├── lib/utils.ts        # cn() class merger (clsx + tailwind-merge)
├── App.tsx             # Root + hash-based routing (256 lines, main state hub)
└── main.tsx            # Vite entry point
```

## WHERE TO LOOK

| Task | Location |
|------|----------|
| Add API endpoint call | `services/api.ts` |
| Add new page | `pages/` + update `App.tsx` routing |
| Create UI component | `components/ui/` (primitives) |
| Add feature component | `components/{feature}/` folder |
| Modify presentation UI | `components/presentation/` |
| RAG document handling | `components/rag/` |
| Change styling | Component file (Tailwind classes) |
| Add TypeScript types | `types/` |
| Error handling utils | `utils/errorHandler.ts` |
| File URL generation | `utils/fileUrls.ts` |

## PATTERNS

### State Management
- **Local only**: `useState`, `useEffect`, `useCallback`
- **No global state**: No Redux, Zustand, or Context providers
- **Props drilling**: State passed down via props from App.tsx
- **App.tsx is state hub**: Sidebar state, selected chat, current slide, presentations list all live here

### Styling
- **TailwindCSS utility classes** for all styling
- **`cn()` helper** for conditional class merging
- **Custom palette**: background #0a0a0f, primary #6366f1, etc.
- **One exception**: `SimplifiedDocumentViewer.css` for PDF viewer
- **tailwindcss-animate** plugin for animations
- **Custom glow keyframes** in tailwind.config.ts

### API Integration
- **Service layer**: All calls through `services/api.ts`
- **Toast feedback**: `toast.promise()` from sonner
- **Error handling**: try/catch with console.error + `utils/errorHandler.ts`
- **Loading states**: Boolean flags in component state
- **SSE**: EventSource via `services/sse.ts` for document processing progress

### Routing
- **Hash-based**: Custom `useHashRoute` hook in App.tsx, not React Router
- **Routes**: `#/` (home/workspace), `#/documents` (library)
- **Keyboard shortcut**: `Ctrl+B` toggles sidebar

### Icons
- **HugeIcons**: `<HugeiconsIcon icon={...} />` pattern (primary)
- **Lucide**: Secondary icon set

### Key Components
- **GenerateButton** (234 lines): Expandable generation form with theme selection, doc attachment, file type toggle
- **DocumentLibrary** (329 lines): Full document management with drag-drop upload, SSE progress tracking
- **Sidebar** (182 lines): Presentation history with relative time, delete functionality

## CONVENTIONS

- **Path alias**: `@/` → `src/` (`import { Button } from '@/components/ui/button'`)
- **Strict TypeScript**: All strict flags enabled (`noUnusedLocals`, `verbatimModuleSyntax`, `erasableSyntaxOnly`)
- **Feature folders**: Group by domain (presentation/, rag/, layout/)
- **Radix UI**: Headless primitives for select, switch, progress
- **Barrel exports**: `components/rag/index.ts` re-exports

## ANTI-PATTERNS

- **NO `as any`** — Strict mode enforced
- **NO empty catch blocks** — Some exist, need cleanup
- **NO hardcoded URLs** — Use `VITE_API_BASE_URL` env var
- **NO CSS-in-JS** — TailwindCSS only
- **NO direct fetch** — Use service layer (`services/api.ts`)
