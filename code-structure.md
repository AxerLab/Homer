├─ pyproject.toml
├─ uv.lock
├─ README.md
├─ .gitignore
├─ .env.example
├─ scripts/
│  ├─ run_local.sh
│  ├─ format.sh
│  └─ lint.sh
├─ frontend/
│  ├─ package.json
│  ├─ package-lock.json
│  ├─ tsconfig.json
│  ├─ tsconfig.node.json
│  ├─ vite.config.ts
│  ├─ tailwind.config.ts
│  ├─ postcss.config.js
│  ├─ components.json          # shadcn/ui configuration
│  ├─ index.html
│  ├─ public/
│  │  ├─ favicon.ico
│  │  └─ assets/
│  ├─ src/
│  │  ├─ main.tsx              # React app entry point
│  │  ├─ App.tsx               # Root component with router
│  │  ├─ index.css             # Global styles and Tailwind directives
│  │  ├─ vite-env.d.ts
│  │  ├─ routes/               # TanStack Router route definitions
│  │  │  ├─ __root.tsx         # Root layout component
│  │  │  ├─ index.tsx          # Home/landing page
│  │  │  ├─ dashboard.tsx      # Main dashboard view
│  │  │  ├─ editor.tsx         # Slide editor interface
│  │  │  └─ preview.tsx        # Presentation preview
│  │  ├─ components/           # React components
│  │  │  ├─ ui/                # shadcn/ui base components
│  │  │  │  ├─ button.tsx
│  │  │  │  ├─ card.tsx
│  │  │  │  ├─ dialog.tsx
│  │  │  │  ├─ dropdown-menu.tsx
│  │  │  │  ├─ input.tsx
│  │  │  │  ├─ label.tsx
│  │  │  │  ├─ select.tsx
│  │  │  │  ├─ textarea.tsx
│  │  │  │  ├─ toast.tsx
│  │  │  │  └─ ...             # Other shadcn components as needed
│  │  │  ├─ layout/            # Layout components
│  │  │  │  ├─ Header.tsx
│  │  │  │  ├─ Sidebar.tsx
│  │  │  │  └─ Footer.tsx
│  │  │  ├─ editor/            # Editor-specific components
│  │  │  │  ├─ SlideCanvas.tsx
│  │  │  │  ├─ SlidePanel.tsx
│  │  │  │  ├─ ToolBar.tsx
│  │  │  │  └─ PropertiesPanel.tsx
│  │  │  ├─ preview/           # Preview components
│  │  │  │  ├─ PresentationViewer.tsx
│  │  │  │  └─ SlideNavigator.tsx
│  │  │  └─ shared/            # Shared/common components
│  │  │     ├─ LoadingSpinner.tsx
│  │  │     ├─ ErrorBoundary.tsx
│  │  │     └─ PromptInput.tsx
│  │  ├─ hooks/                # Custom React hooks
│  │  │  ├─ usePresentation.ts
│  │  │  ├─ useSlideEditor.ts
│  │  │  └─ useAPI.ts
│  │  ├─ lib/                  # Utility functions and helpers
│  │  │  ├─ utils.ts           # General utilities (cn() for classnames, etc.)
│  │  │  ├─ api.ts             # API client/fetch wrappers
│  │  │  └─ constants.ts       # App-wide constants
│  │  ├─ types/                # TypeScript type definitions
│  │  │  ├─ presentation.ts
│  │  │  ├─ slide.ts
│  │  │  └─ api.ts
│  │  ├─ store/                # State management (if needed)
│  │  │  ├─ presentationStore.ts
│  │  │  └─ editorStore.ts
│  │  └─ styles/               # Additional styles if needed
│  │     └─ themes.ts          # Theme configuration
├─ src/
│  ├─ aislides/
        main.py # basic entrypoint
        config/ # env var loading code and logging
        core/
            models/ # data structures for slide components
            llm/ # llm wrappers
            agent/ # pydantic agent definitions
                agent.py # core agent initilization
                prompts.py # agent prompts
            tools/
            slide_generator/ # slide generator code (prompt to JSON)
            engines/
                tex/
                pptx/
                pdf/
        api/ # endpoints (explore gRPC)
├─ tests/
│  ├─ aislides/
        end_to_end.py
        config/ # env var loading code
        core/
            models/ # test slide components
            llm/ # test llm wrappers
            slide_generator/ # test slide generator code (prompt to JSON)
            engines/
                tex/
                pptx/
                pdf/
        api/ # test endpoints
