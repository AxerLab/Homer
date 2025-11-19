# VISUAL_DESIGN_SPECIFICATION_COMPLETE

## UI_OVERVIEW_DESCRIPTION
Application: AI-powered presentation generator with dark theme
Layout: 4-panel design - Left sidebar, Top header, Center canvas, Right panel
Theme: Dark professional with indigo accent (#6366f1)
Typography: System fonts, no custom fonts
Style: Modern, minimal, glass-morphism effects

## EXACT_VISUAL_LAYOUT

### VIEWPORT_1440x1024_STRUCTURE
```
┌─────────────────────────────────────────────────────────┐
│ HEADER (h:64px, w:full, bg:#0a0a0f)                      │
├────────┬────────────────────────────┬────────────────────┤
│SIDEBAR │   MAIN CANVAS AREA         │ RIGHT PANEL        │
│w:256px │   (flex-1, centered)       │ w:384px           │
│bg:#13131a   bg:#0a0a0f             │ bg:#13131a        │
│        │   ┌──────────────┐         │                   │
│8 items │   │SLIDE PREVIEW  │         │ - Title section   │
│list    │   │aspect 16:10   │         │ - Content boxes   │
│        │   │gradient gray  │         │ - Quick actions   │
│        │   └──────────────┘         │ - Input at bottom │
│        │                             │                   │
│        │  [Generate... button]       │                   │
│        │   (floating, centered)      │                   │
└────────┴────────────────────────────┴────────────────────┘
```

## COMPONENT_VISUAL_SPECIFICATIONS

### 1_SIDEBAR_VISUAL
- Background: #13131a (elevated)
- Width: 256px fixed
- Border-right: 1px solid #1e293b
- Toggle button:
  - Position: 80px from top (top-20)
  - Size: 40x32px approx
  - Icon: ChevronLeft/Right 20x20px
  - Bg: #13131a with border #1e293b
  - Hover: 10% primary overlay
- Past Chats heading:
  - Font-size: 18px (text-lg)
  - Font-weight: 600
  - Color: #f8fafc
  - Margin-bottom: 16px
- Chat items:
  - Height: 48px each
  - Padding: 12px 16px
  - Border-radius: 8px
  - Default: transparent bg, #94a3b8 text
  - Hover: 10% primary bg, #f8fafc text
  - Selected: 20% primary bg, #f8fafc text
  - Gap between: 8px

### 2_HEADER_VISUAL
- Height: 64px exact
- Background: #0a0a0f
- Border-bottom: 1px solid #1e293b
- Content layout:
  - Left: "Slide Title" input/text
  - Center: Navigation (◀ 1/10 ▶)
  - Right: 4 option buttons
- Navigation styling:
  - Buttons: 32x32px
  - Numbers: white on disabled, clickable when enabled
  - Divider: "/" in #94a3b8
- Option buttons:
  - Text: 14px, #94a3b8
  - Padding: 6px 12px
  - Hover: text becomes #f8fafc, 10% primary bg

### 3_MAIN_CANVAS_AREA
- Background: #0a0a0f (main background)
- Padding: 32px all sides
- Slide preview:
  - Max-width: 1024px
  - Aspect ratio: 16:10 (CRITICAL)
  - Background: linear-gradient(180deg, #374151 0%, #1f2937 100%)
  - Border-radius: 8px
  - Shadow: 0 25px 50px -12px rgba(0,0,0,0.25)
  - Content padding: 32px
  - Title: 30px bold white
  - Content: 18px #e5e7eb

### 4_RIGHT_PANEL_VISUAL
- Width: 384px fixed
- Background: #13131a
- Border-left: 1px solid #1e293b
- Structure:

  a) Header section (p:16px, border-bottom):
     - Title: 18px medium #f8fafc
     - No counter here (removed duplicate)

  b) Content area (flex-1, p:16px):
     - Box 1: bg:#0a0a0f/50, border:#1e293b, rounded:8px, p:16px
       Text: 14px, #94a3b8
     - Box 2: Same styling, longer content
     - AI Overview button: right-aligned, 12px, #94a3b8
       Icon: 12x12px sparkle

  c) Bottom section (p:16px, border-top):
     - Quick actions: 4 chips
       Size: height 24px, px:12px py:4px
       Bg: 10% primary
       Text: 12px, 70% white
       Border-radius: full (9999px)
       Gap: 8px
       Hover: 20% primary bg

     - Input area:
       Height: ~68px (2 rows + padding)
       Bg: #0a0a0f/50
       Border: 1px solid #1e293b
       Border-radius: 8px
       Padding: top:12px, bottom:40px, left:16px, right:80px
       Placeholder: #94a3b8/50
       Buttons positioned bottom:8px right:8px

### 5_GENERATE_BUTTON_STATES

#### Collapsed state:
- Size: px:32px py:16px
- Background: #6366f1
- Text: "Generate..." white 600 weight
- Border-radius: 12px
- Shadow: 0 10px 15px -3px rgba(0,0,0,0.1)
- Hover: 90% opacity, larger shadow
- Position: bottom:32px, centered horizontally

#### Expanded state:
- Width: 500px min
- Background: #13131a/95 with backdrop-blur
- Border: 1px solid #6366f1/30
- Border-radius: 16px
- Padding: 24px
- Shadow: 0 25px 50px -12px rgba(0,0,0,0.25)
- Glow effect: before pseudo-element with gradient blur

- Textarea:
  Height: 96px
  Bg: #0a0a0f/50
  Border: 1px #1e293b
  Radius: 8px
  Padding: 12px 16px

- Format selector:
  Container: bg:#0a0a0f/50, rounded-full, p:4px
  Buttons: 14px text, px:16px py:6px
  Selected: bg:#6366f1, white text, shadow
  Unselected: #94a3b8 text

- Cancel/Send button:
  Cancel: text only, #94a3b8
  Send: bg:#6366f1, white, with icon, px:16px py:8px

## COLOR_APPLICATION_MAP
```
ELEMENT                 | COLOR
------------------------|------------------
Main background         | #0a0a0f
Elevated surfaces       | #13131a
All borders            | #1e293b
Primary actions        | #6366f1
Primary text           | #f8fafc
Secondary text         | #94a3b8
Muted backgrounds      | #1e293b
Hover overlays         | primary/10 or /20
Active states          | primary/20 or /30
Slide canvas gradient  | #374151 to #1f2937
Input placeholders     | #94a3b8/50
```

## SPACING_SYSTEM
```
Component gaps: 8px (gap-2)
Section padding: 16px (p-4)
Large padding: 32px (p-8)
Button padding: 12px horizontal, 6-8px vertical
Border radius: 8px standard, 12px buttons, full for chips
List item gaps: 8px
Header height: 64px
Toggle position: 80px from top
```

## INTERACTION_STATES

### Hover effects:
- Buttons: background opacity change + color shift
- List items: background overlay + text color change
- Links: text color shift from muted to full
- All transitions: 200-300ms ease

### Focus states:
- Inputs: border color to primary/50
- Buttons: outline-none (handled by color change)
- Textarea: border primary/50

### Active states:
- Selected chat: bg-primary/20
- Selected format: bg-primary with shadow
- Clicked buttons: scale 0.98 briefly

## TYPOGRAPHY_HIERARCHY
```
Heading (Past Chats): 18px semibold
Slide title canvas: 30px bold
Slide content: 18px normal
Panel title: 18px medium
Body text: 14px normal
Small text/chips: 12px normal
Button text: 14px medium
Input text: 14px normal
Navigation: 24px for numbers
```

## SHADOWS_AND_EFFECTS
```
Slide canvas: shadow-2xl (0 25px 50px -12px)
Generate button: shadow-lg hover:shadow-xl
Expanded dialog: shadow-2xl + glow effect
Format selector active: shadow-lg
Glass effect: backdrop-blur-lg with /95 opacity
Border glow: 0 0 20-30px with primary/30-50
```

## CRITICAL_VISUAL_DETAILS

1. **NO ROUNDED CORNERS** on main containers - only internal elements
2. **ASPECT RATIO 16:10** for slide preview - NOT 16:9
3. **GRADIENT DIRECTION** top-to-bottom for slide (gray-700 to gray-800)
4. **TOGGLE BUTTON** stays at top-20 (80px) NOT top-4 (16px)
5. **NO DUPLICATE COUNTERS** - only one "1/10" in header
6. **TEXTAREA NOT INPUT** for modification prompt in right panel
7. **BUTTONS AT BOTTOM** of textarea, not centered vertically
8. **FORMAT SELECTOR** as unified pill, not separate buttons
9. **SEND BUTTON APPEARS** when text exists, replaces Cancel
10. **CLICK OUTSIDE CLOSES** the Generate dialog

## MOCK_CONTENT_EXACT

Slide title: "Introduction to AI"
Slide content: "This slide provides an overview of artificial intelligence and its applications in modern technology."

Lorem text for panel: "Fusce nec rutrum velit. In vitae ex cursus, condimentum mi at, aliquet lorem. Integer ornare tellus augue, at lacinia elit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer ornare tellus augue, in mauris non faucibus volutpat et velit ligula. Donec feugiat quam vel, aute mauris lacinia aliquam ornare. Sed finibus mauris non felis ultricies tincidunt. Fusce sem tellus, fringilla eget sapien sed, ornare maximus ligula."

Past chats list (8 items):
1. "Pitch meeting 24th"
2. "Client Demo"
3. "Hackathon Deck"
4. "AI brainstorming"
5. "Financial Meeting"
6. "Board meeting deck"
7. "School project"
8. "History presentation"

Quick actions: ["Add Detail", "Simplify", "Add Examples", "Change tone"]

## FINAL_VISUAL_RESULT
Dark professional presentation editor with:
- Clean minimal interface
- Indigo accent color (#6366f1)
- 4-panel layout
- Smooth animations (300ms)
- Glass morphism effects on dialogs
- Consistent spacing and alignment
- No custom fonts (system stack)
- Professional gradient on slide preview
- Subtle shadows and borders
- Clear visual hierarchy

END_VISUAL_SPEC