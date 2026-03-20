# Design System Documentation

**Aesthetic:** Industrial + Scientific
**Purpose:** Satellite monitoring for precision agriculture
**Target Audience:** Farm operators, customers valuing transparency, technical stakeholders

---

## Design Principles

### 1. **Precision & Authority**
Data-driven design that emphasizes technical credibility. Every element serves the purpose of communicating scientific measurements with clarity and confidence.

### 2. **Minimalism & Function**
Remove decoration that doesn't serve a purpose. Use borders, not shadows. Use tables, not card grids. Typography and layout create hierarchy, not visual effects.

### 3. **Technical Honesty**
Monospace typography for data values. Uppercase labels. Precise measurements. No emojis or playful elements - this is a research-grade monitoring system.

### 4. **Accessibility First**
Semantic HTML, ARIA labels, keyboard navigation, sufficient contrast, reduced motion support. Everyone should be able to access farm health data.

---

## Typography

### Font Families

```css
--font-display: 'Space Grotesk'     /* Geometric, technical, headings */
--font-body: System UI stack         /* Readable, body text */
--font-mono: 'JetBrains Mono'       /* Data values, labels, code */
```

**Space Grotesk** provides a modern, geometric aesthetic for headings. Use for:
- Page titles
- Section headings
- Emphasized text

**System UI** provides maximum readability for body content. Use for:
- Paragraphs
- Descriptions
- Long-form text

**JetBrains Mono** provides technical precision for data. Use for:
- Numeric values
- Timestamps
- Labels
- Technical identifiers

### Type Scale (1.125 ratio)

```
xs:   12px - Labels, captions
sm:   14px - Secondary text
base: 16px - Body text
md:   18px - Emphasized text
lg:   20px - h3
xl:   23px - h2
2xl:  26px - h1
3xl:  29px - Hero text
```

### Usage Guidelines

- **All caps + letter-spacing** for labels and metadata
- **Bold + tight letter-spacing** for headings
- **Monospace for all data values** (health scores, measurements, dates)

---

## Color System

### Neutral Palette (Cool Gray - Technical)

```
50:  #f8f9fa - Background
100: #e9ecef - Surface raised
200: #dee2e6 - Subtle borders
300: #ced4da - Borders
400: #adb5bd - Disabled text
500: #6c757d - Secondary text
600: #495057 - Body text
700: #343a40 - Emphasized text
800: #212529 - Headings
900: #0d1117 - Maximum contrast
```

### Accent Color (Data Blue)

```
data:        #0969da - Primary actions, links
data-light:  #54aeff - Hover states
data-dark:   #033d8b - Active states
data-subtle: #ddf4ff - Backgrounds, selections
```

### Semantic Colors

```
success: #2da44e - Healthy status
warning: #bf8700 - Warning status
danger:  #cf222e - Critical alerts
info:    #0969da - Informational
```

### Health Score Gradient

```
critical:   #cf222e - 0-30
poor:       #fb8500 - 30-50
fair:       #bf8700 - 50-70
good:       #2da44e - 70-90
excellent:  #116329 - 90-100
```

### Usage Guidelines

- **Never use pure black or white** - always tint neutrals
- **Tint text toward background color** instead of using gray
- **Use monospace font with colors** for data values
- **Borders, not shadows** for elevation

---

## Spacing System (8px base)

```
0: 0
1: 4px   - Tight internal spacing
2: 8px   - Base unit
3: 12px  - Related elements
4: 16px  - Component padding
5: 24px  - Section spacing
6: 32px  - Major sections
7: 48px  - Page sections
8: 64px  - Hero spacing
9: 96px  - Large gaps
```

### Guidelines

- **Use spacing tokens, never arbitrary values**
- **Vary spacing for visual rhythm** - not the same padding everywhere
- **Tight groupings** for related data (space-2 to space-3)
- **Generous separation** for sections (space-5 to space-6)

---

## Layout Patterns

### Container

```
max-width: 1600px
padding: var(--space-6) - 32px
```

### Grid System

**Two-column layout (content + sidebar):**
```css
grid-template-columns: 1fr minmax(320px, 400px);
gap: var(--space-5);
```

### Component Spacing

- **Card grids:** Use tables or lists instead
- **Stat displays:** Border-separated table layout
- **Zone selector:** Vertical list with left border accent
- **Charts:** Full-width containers with internal padding

---

## Borders & Elevation

### Border System

```
width:       1px (default)
width-thick: 2px (emphasis)
style:       solid
radius-sm:   2px (minimal)
radius-md:   4px (standard)
radius-lg:   6px (large containers)
```

### Elevation

**Use borders, not shadows:**
- Primary containers: `border: 1px solid var(--color-border)`
- Active/selected: `border-left: 3px solid var(--color-data)`
- Emphasis: `border: 2px solid var(--color-border-emphasis)`

**Rare shadow usage:**
```css
shadow-sm: 0 1px 2px rgba(13, 17, 23, 0.08)
shadow-md: 0 2px 4px rgba(13, 17, 23, 0.1)
shadow-lg: 0 4px 8px rgba(13, 17, 23, 0.12)
```

Use shadows only for:
- Dropdown menus
- Modals/overlays
- Tooltips

---

## Motion

### Duration

```
instant: 0ms   - No transition
fast:    100ms - Subtle feedback
base:    200ms - Standard transitions
slow:    300ms - Emphasized changes
```

### Easing

```
ease-out:    cubic-bezier(0.33, 1, 0.68, 1)      /* Deceleration */
ease-in-out: cubic-bezier(0.65, 0, 0.35, 1)     /* Smooth */
```

### Guidelines

- **Never use bounce or elastic** - scientific aesthetic requires precision
- **Animate transform and opacity only** - not layout properties
- **Wrap animations in @media (prefers-reduced-motion: no-preference)**
- **Keep duration fast** - 100-200ms for most interactions

---

## Component Patterns

### Data Display

**Use technical formatting:**
```jsx
<div className="info-item">
  <span className="info-label">LATEST NDVI</span>
  <span className="info-value text-mono">0.742</span>
</div>
```

### Buttons

**Technical style:**
```css
padding: var(--space-3) var(--space-5);
font-family: var(--font-mono);
text-transform: uppercase;
letter-spacing: var(--letter-spacing-wide);
border: 1px solid var(--color-data);
```

### Lists (Not Cards)

**Zone selector pattern:**
```css
/* Vertical list */
flex-direction: column;
gap: 0;

/* Items with left border accent */
border-left: 3px solid transparent;

/* Active state */
border-left-color: var(--color-data);
background: var(--color-data-subtle);
```

### Tables (Not Grids)

**Stat display pattern:**
```css
display: grid;
grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
gap: 0;
border: 1px solid var(--color-border);

/* Items with right border separation */
.stat-card {
  border-right: 1px solid var(--color-border);
}
```

---

## Accessibility

### Semantic HTML

```html
<header> - Dashboard header
<nav>    - Farm selector
<main>   - Main content area
<aside>  - Sidebar with alerts
<footer> - Footer with metadata
```

### ARIA Labels

**Interactive elements:**
```html
<button aria-selected="true" role="tab">...</button>
<div role="region" aria-labelledby="heading-id">...</div>
<div role="status" aria-live="polite">...</div>
```

**Charts:**
```html
<div role="img" aria-label="Time series chart showing health metrics">
  <canvas />
</div>
```

### Focus States

```css
*:focus-visible {
  outline: 2px solid var(--color-data);
  outline-offset: 2px;
}
```

### Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Dark Mode

Colors automatically adapt using `@media (prefers-color-scheme: dark)`:

- Neutrals invert (50 becomes 900, etc.)
- Accent colors become lighter
- Borders remain visible with adjusted opacity
- Shadows become darker

All design tokens work in both modes - no component changes needed.

---

## Anti-Patterns to Avoid

❌ **Card grids** - Use tables or lists
❌ **Glassmorphism** - Use solid backgrounds
❌ **Gradient backgrounds** - Use solid colors
❌ **Drop shadows everywhere** - Use borders
❌ **Rounded corners (8px)** - Use minimal radius (2-4px)
❌ **Emojis** - Use text labels or icons
❌ **Bouncing animations** - Use linear/ease-out only
❌ **Hard-coded colors** - Use design tokens
❌ **Gray text on colored backgrounds** - Use tinted colors

---

## File Structure

```
src/
├── design-system.css       # Design tokens (import this first)
├── index.css               # Base styles
└── components/
    ├── Dashboard.css       # Component-specific styles
    ├── Dashboard.jsx       # React component
    └── ...
```

**Import order:**
1. Google Fonts (in index.html or index.css)
2. design-system.css (tokens)
3. index.css (base styles)
4. Component CSS files

---

## Quick Reference

### Common Patterns

**Data label + value:**
```html
<div className="info-item">
  <span className="info-label text-mono">LABEL</span>
  <span className="info-value text-mono">value</span>
</div>
```

**Technical heading:**
```html
<h2 className="text-display">Section Title</h2>
<p className="text-mono" style="text-transform: uppercase">
  TECHNICAL SUBTITLE
</p>
```

**Border-accented list item:**
```css
border-left: 3px solid var(--color-data);
padding: var(--space-4);
background: var(--color-surface);
```

---

## Resources

- [Space Grotesk Font](https://fonts.google.com/specimen/Space+Grotesk)
- [JetBrains Mono Font](https://fonts.google.com/specimen/JetBrains+Mono)
- [Sentinel-2 Satellite Specifications](https://sentinel.esa.int/web/sentinel/missions/sentinel-2)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

---

**Last Updated:** 2026-03-19
**Version:** 1.0.0
**Maintained by:** Design System Team
