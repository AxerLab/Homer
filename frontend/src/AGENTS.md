# FRONTEND SOURCE

React 18 + Vite + TailwindCSS presentation generator UI.

## STRUCTURE

```
src/
├── components/
│   ├── presentation/   # SlideCanvas, SlideNavigator, GenerateButton, SlideContentPanel
│   ├── layout/         # Sidebar, Header, MainLayout, HamburgerMenu
│   ├── rag/            # DocumentUpload, DocumentAttachSelector, DocumentProgressCard
│   ├── viewer/         # DocumentViewer, SimplifiedDocumentViewer (PDF display)
│   ├── editor/         # SlideEditor
│   ├── ui/             # Primitives: button, card, select, progress, badge, switch
│   └── onboarding/     # OnboardingStep, FirstTimeTooltip
├── pages/              # Workspace, DocumentLibrary, HomePage, NotFound
├── services/
│   ├── api.ts          # presentationApi, ragApi (329 lines)
│   └── sse.ts          # Server-sent events for document progress
├── types/              # TypeScript interfaces (api.ts, presentation.ts)
├── lib/utils.ts        # cn() class merger (clsx + tailwind-merge)
├── App.tsx             # Root + hash-based routing
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

## PATTERNS

### State Management
- **Local only**: `useState`, `useEffect`, `useCallback`
- **No global state**: No Redux, Zustand, or Context providers
- **Props drilling**: State passed down via props

### Styling
- **TailwindCSS utility classes** for all styling
- **`cn()` helper** for conditional class merging
- **Custom palette**: background #0a0a0f, primary #6366f1, etc.
- **One exception**: `SimplifiedDocumentViewer.css` for PDF viewer

### API Integration
- **Service layer**: All calls through `services/api.ts`
- **Toast feedback**: `toast.promise()` from sonner
- **Error handling**: try/catch with console.error
- **Loading states**: Boolean flags in component state

### Routing
- **Hash-based**: Custom `useHashRoute` hook, not React Router
- **Routes**: `#/` (home), `#/documents` (library)

### Icons
- **HugeIcons**: `<HugeiconsIcon icon={...} />` pattern
- **Lucide**: Secondary icon set

## CONVENTIONS

- **Path alias**: `@/` → `src/` (`import { Button } from '@/components/ui/button'`)
- **Strict TypeScript**: All strict flags enabled
- **Feature folders**: Group by domain (presentation/, rag/, layout/)
- **Radix UI**: Headless primitives for select, switch, progress

## ANTI-PATTERNS

- **NO `as any`** — Strict mode enforced
- **NO empty catch blocks** — Some exist, need cleanup
- **NO hardcoded URLs** — Use `VITE_API_BASE_URL` env var
- **NO CSS-in-JS** — TailwindCSS only
