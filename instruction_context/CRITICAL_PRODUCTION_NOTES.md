# ULTRA_CRITICAL_PRODUCTION_REQUIREMENTS

## FILE_CREATION_ORDER_MANDATORY
```
1. npm create vite@latest frontend -- --template react-ts
2. cd frontend
3. REPLACE package.json BEFORE npm install
4. npm install
5. CREATE ALL CONFIG FILES:
   - vite.config.ts (with @ alias)
   - tailwind.config.ts (exact colors)
   - postcss.config.js
   - tsconfig.json (with paths)
   - tsconfig.node.json
6. REPLACE index.html
7. CREATE src/index.css
8. CREATE folder structure:
   mkdir -p src/components/layout
   mkdir -p src/components/presentation
   mkdir -p src/lib
   mkdir -p src/types
9. CREATE src/lib/utils.ts FIRST
10. CREATE src/types/presentation.ts
11. CREATE components in order:
    - Sidebar.tsx
    - SlideNavigator.tsx
    - Header.tsx
    - SlideCanvas.tsx
    - SlideContentPanel.tsx
    - GenerateButton.tsx
12. CREATE App.tsx
13. CREATE main.tsx
14. npm run dev
15. OPEN at http://localhost:5173
16. SET viewport to 1440x1024
```

## TYPESCRIPT_ERROR_FIXES
```typescript
// If "Cannot find module '@/lib/utils'" error:
// CHECK: vite.config.ts has alias
// CHECK: tsconfig.json has paths
// RESTART: dev server after config changes

// If "Property does not exist" errors:
// CHECK: All interfaces imported correctly
// CHECK: Types file created first

// If "JSX element type" errors:
// CHECK: All components exported as named exports
// CHECK: React imported in every component file
```

## CSS_CLASS_CONFLICTS_PREVENTION
```css
/* NEVER use these Tailwind classes together: */
/* WRONG: */ "bg-black bg-opacity-50"
/* RIGHT: */ "bg-black/50"

/* WRONG: */ "text-white opacity-70"
/* RIGHT: */ "text-white/70"

/* WRONG: */ "w-full max-w-full"
/* RIGHT: */ "w-full"

/* WRONG: */ "flex flex-row"
/* RIGHT: */ "flex"

/* WRONG: */ "p-4 px-4 py-4"
/* RIGHT: */ "p-4"
```

## STATE_SYNCHRONIZATION_CRITICAL
```typescript
// Generate Button must clear prompt on close:
const handleClose = () => {
  setIsExpanded(false)
  setPrompt('') // CRITICAL: Clear prompt
}

// Generate Button must clear after send:
const handleGenerate = () => {
  if (prompt.trim()) {
    onGenerate(prompt, selectedFormat)
    setPrompt('') // CRITICAL: Clear after send
    setIsExpanded(false)
  }
}

// Sidebar state persists:
// DO NOT reset selectedChatId when closing sidebar
// DO NOT change isSidebarOpen on route changes
```

## EXACT_PIXEL_VALUES_REFERENCE
```
256px = w-64 (sidebar width)
384px = w-96 (right panel width)
1024px = max-w-4xl (slide canvas max width)
64px = h-16 (header height)
80px = top-20 (toggle button position)
32px = p-8 (large padding)
16px = p-4 (standard padding)
8px = gap-2 (standard gap)
500px = min-w-[500px] (generate dialog)
```

## MOTION_FRAMER_EXACT_VALUES
```typescript
// ONLY for Generate button dialog:
initial={{ opacity: 0, scale: 0.9, y: 20 }}
animate={{ opacity: 1, scale: 1, y: 0 }}
exit={{ opacity: 0, scale: 0.9, y: 20 }}
// NO transition prop needed, uses defaults
// NO other animations in the app
```

## DEV_SERVER_REQUIREMENTS
```bash
# MUST use Vite dev server
npm run dev
# NOT npm start
# NOT npx vite
# Port 5173 default
# If port taken, will use 5174
```

## ABSOLUTE_FORBIDDEN_PATTERNS
```typescript
// NEVER:
const [isDarkMode] // NO THEME SWITCHING
useContext() // NO CONTEXT API
useReducer() // NO REDUCERS
fetch() // NO API CALLS
axios // NO HTTP LIBRARIES
localStorage // NO PERSISTENCE
sessionStorage // NO SESSION
document.getElementById // USE React refs
window.addEventListener // EXCEPT for mousedown in Generate
CSS modules // USE Tailwind only
styled-components // USE Tailwind only
.scss/.sass files // USE .css only
```

## CONSOLE_OUTPUT_EXPECTED
```javascript
// Expected console.log on Generate:
console.log('Generating presentation:', { prompt: "...", format: "PPTX" })

// Expected warning (IGNORE):
"Warning: You provided a `value` prop to a form field without an `onChange` handler"

// NO other console output should appear
// NO errors should appear
```

## FINAL_VERIFICATION_STEPS
```
1. Open http://localhost:5173
2. Set browser zoom to 100%
3. Set viewport width to exactly 1440px
4. Verify sidebar is open on load
5. Click sidebar toggle - should slide smooth
6. Click Generate button - should expand centered
7. Type in Generate box - Cancel becomes Send
8. Click outside Generate box - should close
9. Click format options - selected shows blue
10. Check right panel textarea - placeholder visible
11. Verify NO duplicate "1/10" counters
12. Verify slide canvas has gradient
13. Verify all text colors correct
14. Open DevTools - no red errors in console
15. Network tab - no failed requests
```

## DEPLOYMENT_BUILD_COMMAND
```bash
npm run build
# Creates dist/ folder
# DO NOT modify build output
# DO NOT add base path
# Serve from root domain only
```

## COLORS_HEX_TO_TAILWIND_MAP
```
#0a0a0f → bg-background
#13131a → bg-elevated
#6366f1 → bg-primary, text-primary
#f8fafc → text-text
#94a3b8 → text-text-muted
#1e293b → border-border
#374151 → from-gray-700
#1f2937 → to-gray-800
```

## LOREM_IPSUM_TEXT_EXACT
```
First box: "This slide provides an overview of artificial intelligence and its applications in modern technology."

Second box: "Fusce nec rutrum velit. In vitae ex cursus, condimentum mi at, aliquet lorem. Integer ornare tellus augue, at lacinia elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer ornare tellus augue, in mauris non faucibus volutpat et velit ligula. Donec feugiat quam vel, aute mauris lacinia aliquam ornare. Sed finibus mauris non felis ultricies tincidunt. Fusce sem tellus, fringilla eget sapien sed, ornare maximus ligula."

NEVER CHANGE THESE TEXTS
```

## IF_NOTHING_APPEARS_CHECKLIST
```
1. Check index.html has <div id="root">
2. Check main.tsx targets 'root'
3. Check App component has default export
4. Check all imports use correct paths
5. Check @ alias is configured in vite.config.ts
6. Check dev server is running
7. Check no syntax errors in console
8. Check network tab loads all files
9. Clear browser cache
10. Restart dev server
```

## SUCCESS_CRITERIA_ABSOLUTE
- [ ] Sidebar slides smoothly
- [ ] Generate button perfectly centered
- [ ] Format selector shows active state
- [ ] Click outside closes dialog
- [ ] Cancel becomes Send with text
- [ ] Right panel textarea has visible placeholder
- [ ] No duplicate counters
- [ ] Slide canvas has gradient background
- [ ] All colors match exactly
- [ ] No console errors
- [ ] All animations smooth
- [ ] Toggle button at correct position
- [ ] Past chats list shows 8 items
- [ ] Quick actions show 4 chips
- [ ] All hover states work

END_CRITICAL_NOTES