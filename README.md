# Tech Stack

## Backend
- **Python** with Pydantic-AI for agent workflows
- **Provider object** defined in config for LLM integration
- **Supported Models**: llama-3.3-70b-versatile

## Frontend
- **React 18+** with TypeScript for type-safe component development
- **Vite** as build tool and dev server for fast HMR and optimized production builds
- **TailwindCSS** for utility-first styling and responsive design
- **TanStack Router** for type-safe routing with data loading and caching capabilities
- **MUI Material UI** for accessible, composable, and customizable UI components
- **Node.js & npm** for package management and tooling
- Other dependencies: three js (for 3D), framer (for parallax animations)

### Color Palette
The UI follows a modern, sleek AI SaaS aesthetic with darker tones and high contrast:
- **Background**: `#0a0a0f` (deep slate) with `#13131a` (elevated surfaces)
- **Primary**: `#6366f1` (vibrant indigo) for CTAs and highlights
- **Secondary**: `#8b5cf6` (electric violet) for accents and hover states
- **Accent**: `#14b8a6` (teal) for success states and secondary actions
- **Text**: `#f8fafc` (off-white primary), `#94a3b8` (muted gray for secondary text)
- **Border**: `#1e293b` (subtle slate) for dividers and component borders
- **Destructive**: `#ef4444` (coral red) for errors and warnings
- **Muted**: `#1e293b` with `#64748b` text for disabled/inactive states

# Versions
## V0 - Prototype/PoC:
### Tasks
- Prompt to JSON rep
- JSON to TeX using LLM
- TeX to export
### Milestone
- First working prototype 
- Pydantic-ai
- provider object to be defined in config
## V0.1 - Alpha:
### Tasks
- Iterative PPT enhancement (page level editing)
- Preview (UI interface)
## V0.2
### Tasks
- Search tool
- Basic RAG (text only, no OCR)
## V0.3
### Tasks
- Peripheral Integration (Google slides, Overleaf)
- Features and buttons for tweaking slide output
### Milestone
- Internal testing and user feedback (soft launch)
## V0.4
### Tasks
- External LaTeX Template support
- Image 

## V0.5 - Beta
### Tasks
- External LaTeX PPT edit support
- Charts support (using CSV)
- Waitlist page
### Milestone
- MVP launch
- Open source
- Start onboarding users
## V0.6 
## V0.7
## V0.8
## V0.9

## V1.0 - Stable

# Claude instructions
start claude: `SHELL=/bin/bash claude`
Note: API keys need to be given before this

# How to run
## Start docker services
```
docker-compose up -d
```

### start backend
Create a seperate terminal
```
uv sync
source .venv/bin/activate
uvicorn main:app
```
### start frontend
Create a seperate terminal
```
cd frontend/
npm install
npm run dev
```
