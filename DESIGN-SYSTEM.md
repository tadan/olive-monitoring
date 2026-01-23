# Olive Farm Monitoring - Design System Documentation

**Created:** 2026-01-23
**Aesthetic:** Natural & Organic (Mediterranean agricultural heritage)
**Typography:** Technical Monospace (precision satellite data)
**Status:** Implemented and Active

---

## Overview

This design system provides a cohesive visual language for the olive farm monitoring dashboard, combining:
- **Natural, earthy color palette** that reflects agricultural heritage and olive cultivation
- **Technical monospace typography** that emphasizes precision and scientific data
- **Consistent spacing, motion, and interaction patterns** across all components

---

## Color Palette

### Primary - Olive Green
Warm, natural olive tones that reflect the agricultural context.

```css
--color-olive-900: oklch(0.35 0.06 125)  /* Deep olive-brown */
--color-olive-800: oklch(0.42 0.07 125)  /* Dark olive */
--color-olive-700: oklch(0.50 0.08 125)  /* Rich olive */
--color-olive-600: oklch(0.58 0.09 125)  /* Main olive */
--color-olive-500: oklch(0.65 0.08 125)  /* Light olive */
--color-olive-400: oklch(0.72 0.06 125)  /* Muted olive */
--color-olive-300: oklch(0.80 0.04 125)  /* Pale olive */
```

**Usage:**
- Headers, primary buttons, interactive elements
- Vegetation health indicators
- Focus states and active states

### Neutrals - Warm Stone
Earth-toned grays with brown/tan undertones for natural warmth.

```css
--color-stone-50: oklch(0.98 0.003 70)   /* Almost white with warmth */
--color-stone-100: oklch(0.95 0.005 70)  /* Very light warm gray */
--color-stone-200: oklch(0.88 0.008 70)  /* Light stone */
--color-stone-300: oklch(0.78 0.010 70)  /* Medium-light stone */
--color-stone-400: oklch(0.65 0.012 70)  /* Medium stone */
--color-stone-500: oklch(0.52 0.013 70)  /* True stone */
--color-stone-600: oklch(0.42 0.012 70)  /* Dark stone */
--color-stone-700: oklch(0.35 0.010 70)  /* Deeper stone */
--color-stone-800: oklch(0.28 0.008 70)  /* Very dark stone */
--color-stone-900: oklch(0.20 0.005 70)  /* Near black with warmth */
```

**Usage:**
- Text colors (primary, secondary, tertiary)
- Borders and dividers
- Background layers
- Disabled states

### Semantic Colors

```css
--color-success: var(--color-olive-600)      /* Healthy vegetation */
--color-warning: oklch(0.68 0.12 50)         /* Terracotta/clay */
--color-error: oklch(0.50 0.15 25)           /* Deep red-brown */
--color-info: oklch(0.58 0.08 230)           /* Warm slate blue */
```

### Health Status Colors (Map Zones)

```css
--color-health-excellent: oklch(0.65 0.10 130)   /* Rich green (≥70) */
--color-health-good: oklch(0.72 0.09 120)        /* Light olive (≥50) */
--color-health-warning: oklch(0.70 0.13 60)      /* Warm amber (≥30) */
--color-health-poor: oklch(0.64 0.15 45)         /* Clay orange (≥15) */
--color-health-critical: oklch(0.52 0.16 30)     /* Rust red (<15) */
--color-health-nodata: var(--color-stone-400)    /* Neutral gray */
```

### Data Visualization Colors

```css
--color-data-ndvi: var(--color-olive-600)        /* NDVI - olive */
--color-data-ndmi: oklch(0.58 0.10 215)          /* NDMI - clay blue */
--color-data-arvi: oklch(0.62 0.11 145)          /* ARVI - sage green */
--color-data-osavi: oklch(0.55 0.09 100)         /* OSAVI - forest green */
--color-data-health: var(--color-olive-700)      /* Health score */
```

---

## Typography

### Font Families

**Primary:** IBM Plex Mono (data, headings, technical information)
- Monospace font emphasizes precision and scientific measurement
- Used for: headings, data values, metrics, zone names

**Secondary:** Inter (body text, descriptions)
- Clean sans-serif for readability
- Used for: paragraphs, descriptions, supporting text

```css
--font-mono: 'IBM Plex Mono', 'Roboto Mono', 'Courier New', monospace;
--font-sans: 'Inter', system-ui, -apple-system, sans-serif;
```

### Type Scale (1.2 ratio)

```css
--text-xs: 0.75rem      /* 12px - small labels */
--text-sm: 0.875rem     /* 14px - body small */
--text-base: 1rem       /* 16px - body */
--text-lg: 1.125rem     /* 18px - emphasis */
--text-xl: 1.25rem      /* 20px - subheadings */
--text-2xl: 1.5rem      /* 24px - section headings */
--text-3xl: 2rem        /* 32px - page headings */
--text-4xl: 3rem        /* 48px - hero */
```

### Font Weights

```css
--weight-normal: 400
--weight-medium: 500
--weight-semibold: 600
--weight-bold: 700
```

### Line Heights

```css
--leading-tight: 1.2      /* Headings */
--leading-snug: 1.4       /* Tight text */
--leading-normal: 1.6     /* Body text */
--leading-relaxed: 1.8    /* Loose text */
```

### Usage Examples

```css
/* Heading */
h1 {
  font-family: var(--font-mono);
  font-size: var(--text-3xl);
  font-weight: var(--weight-semibold);
  line-height: var(--leading-tight);
  letter-spacing: var(--tracking-tight);
}

/* Data value */
.stat-value {
  font-family: var(--font-mono);
  font-size: var(--text-3xl);
  font-weight: var(--weight-bold);
}

/* Body text */
p {
  font-family: var(--font-sans);
  font-size: var(--text-base);
  line-height: var(--leading-normal);
}
```

---

## Spacing System

Base unit: **4px (0.25rem)**
Scale: Fibonacci-inspired for natural rhythm

```css
--space-1: 0.25rem   /* 4px */
--space-2: 0.5rem    /* 8px */
--space-3: 0.75rem   /* 12px */
--space-4: 1rem      /* 16px */
--space-5: 1.25rem   /* 20px */
--space-6: 1.5rem    /* 24px */
--space-8: 2rem      /* 32px */
--space-10: 2.5rem   /* 40px */
--space-12: 3rem     /* 48px */
--space-16: 4rem     /* 64px */
--space-20: 5rem     /* 80px */
```

**Guidelines:**
- Use consistent spacing tokens instead of arbitrary values
- Create visual rhythm through varied spacing
- Tight groupings (space-2 to space-4) for related content
- Generous separations (space-8 to space-12) for sections

---

## Visual Effects

### Border Radius

Subtle, organic curves - not too rounded.

```css
--radius-sm: 0.25rem   /* 4px - small elements */
--radius-md: 0.5rem    /* 8px - cards, buttons */
--radius-lg: 0.75rem   /* 12px - larger containers */
--radius-full: 9999px  /* Pills, circular */
```

### Shadows

Soft, natural elevation with subtle depth.

```css
--shadow-sm: 0 1px 2px 0 oklch(0 0 0 / 0.05)
--shadow-md: 0 2px 8px 0 oklch(0 0 0 / 0.08)
--shadow-lg: 0 4px 16px 0 oklch(0 0 0 / 0.10)
--shadow-xl: 0 8px 32px 0 oklch(0 0 0 / 0.12)
```

### Borders

```css
--border-width: 1px
--border-width-thick: 2px
--border-color: var(--color-stone-200)
--border-color-hover: var(--color-olive-400)
```

---

## Motion & Timing

### Duration

```css
--duration-fast: 150ms
--duration-base: 200ms
--duration-slow: 300ms
--duration-slower: 500ms
```

### Easing

Natural, organic motion using exponential curves.

```css
--ease-out: cubic-bezier(0.16, 1, 0.3, 1)      /* Smooth deceleration */
--ease-in: cubic-bezier(0.7, 0, 0.84, 0)       /* Smooth acceleration */
--ease-in-out: cubic-bezier(0.65, 0, 0.35, 1)  /* Smooth both */
```

**Guidelines:**
- Use `ease-out` for most transitions (feels responsive)
- Animate only `transform` and `opacity` (performance)
- Respect `prefers-reduced-motion` preference

---

## Component Patterns

### Cards

White surfaces with subtle shadows and natural borders.

```css
.card {
  background-color: var(--bg-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-color);
  padding: var(--space-6);
}
```

### Buttons

```css
button {
  font-family: var(--font-sans);
  font-size: var(--text-base);
  font-weight: var(--weight-medium);
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-md);
  background-color: var(--interactive-default);
  color: var(--text-on-color);
  transition: all var(--duration-base) var(--ease-out);
  min-height: 44px; /* WCAG minimum touch target */
}

button:hover {
  background-color: var(--interactive-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}
```

### Focus Indicators

```css
*:focus-visible {
  outline: 2px solid var(--focus-ring);
  outline-offset: 2px;
  border-radius: var(--radius-sm);
}
```

---

## Accessibility Features

### Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }

  button:hover {
    transform: none !important;
  }
}
```

### Skip Navigation

```css
.skip-link {
  position: absolute;
  top: -100px;
  /* Shows on focus */
}

.skip-link:focus {
  top: var(--space-4);
}
```

### Screen Reader Only

```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
```

---

## JavaScript API

### Design System Module

Import functions from `design-system.js`:

```javascript
import {
  getHealthColor,
  getHealthBorderColor,
  getAlertColor,
  ChartColors,
  resolveColor,
  colorWithOpacity
} from '../design-system';

// Get health color for map zones
const fillColor = getHealthColor(healthScore); // Returns CSS variable

// Resolve color for Chart.js (needs actual color value)
const chartColor = resolveColor(ChartColors.ndvi); // Returns 'rgb(...)'

// Add opacity to color
const transparentColor = colorWithOpacity(ChartColors.health, 0.1);
```

---

## Migration Notes

### Removed AI Aesthetic Patterns

❌ **Before (AI Slop):**
- Green gradient header: `linear-gradient(135deg, #22c55e, #16a34a)`
- Glassmorphism stat cards: `backdrop-filter: blur(10px)` with `rgba(255, 255, 255, 0.2)`
- Hard-coded Tailwind colors throughout
- Generic system fonts

✅ **After (Natural & Organic):**
- Natural olive gradient: `linear-gradient(180deg, var(--color-olive-700), var(--color-olive-800))`
- Solid earth-toned cards with subtle shadows
- Design token system with 60+ semantic tokens
- IBM Plex Mono + Inter typography

### Files Modified

**Design System Core:**
- `frontend/src/design-tokens.css` (NEW) - 350 lines of design tokens
- `frontend/src/design-system.js` (NEW) - JavaScript API for colors
- `frontend/src/index.css` (REWRITTEN) - Base styles with tokens
- `frontend/index.html` - Added Google Fonts (IBM Plex Mono + Inter)

**Components:**
- `frontend/src/components/Dashboard.css` (REWRITTEN) - 485 lines → All tokens
- `frontend/src/components/FarmMap.css` (NORMALIZED) - Design tokens + Leaflet overrides
- `frontend/src/components/FarmSelector.css` (NORMALIZED) - Design tokens
- `frontend/src/components/AlertViewer.css` (NORMALIZED) - Design tokens
- `frontend/src/components/HealthChart.css` (NORMALIZED) - Design tokens
- `frontend/src/components/HistoricalChart.css` (NORMALIZED) - Design tokens

**JavaScript Updates:**
- `frontend/src/components/FarmMap.jsx` - Use design system color functions
- `frontend/src/components/AlertViewer.jsx` - Use getAlertColor()
- `frontend/src/components/HealthChart.jsx` - Use ChartColors
- `frontend/src/components/HistoricalChart.jsx` - Use ChartColors

---

## Future Enhancements

### Dark Mode Support (Planned)
The design token system is structured to support dark mode:

```css
@media (prefers-color-scheme: dark) {
  :root {
    --bg-canvas: var(--color-stone-900);
    --bg-surface: var(--color-stone-800);
    --text-primary: var(--color-stone-100);
    /* etc. */
  }
}
```

### Component Library Expansion
Consider adding:
- Badge component
- Modal/Dialog component
- Toast notification component
- Data table component

---

## Resources

- **Font:** [IBM Plex Mono on Google Fonts](https://fonts.google.com/specimen/IBM+Plex+Mono)
- **Font:** [Inter on Google Fonts](https://fonts.google.com/specimen/Inter)
- **Color:** [OKLCH Color Picker](https://oklch.com/)
- **Accessibility:** [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

---

**Last Updated:** 2026-01-23
**Maintained By:** Design System Team
