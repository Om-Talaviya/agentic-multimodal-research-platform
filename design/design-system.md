# Design System & Style Guide: design/design-system.md

This document defines the CSS custom properties, color palette, typography, components, and layout utilities implemented in `apps/web/src/index.css`.

---

## 1. Color Palette & Tokens

```css
:root {
  /* Brand & Core */
  --color-primary: #3b82f6;        /* Royal Blue */
  --color-primary-hover: #2563eb;  /* Deep Blue */
  --color-secondary: #64748b;      /* Slate */
  
  /* Canvas & Surfaces */
  --color-background: #f8fafc;     /* Off-white / Cool Grey */
  --color-surface: #ffffff;        /* Pure White Card Surface */
  --color-border: #e2e8f0;         /* Subtle Border Grey */
  
  /* Typography */
  --color-text: #0f172a;           /* Dark Slate Charcoal */
  --color-text-muted: #64748b;     /* Muted Grey */
  
  /* Semantic Statuses */
  --color-success: #10b981;        /* Emerald Green */
  --color-warning: #f59e0b;        /* Amber */
  --color-error: #ef4444;          /* Crimson Red */
  --color-info: #06b6d4;           /* Cyan */
}
```

---

## 2. Spacing, Borders & Shadows

```css
:root {
  /* Spacing Scale */
  --spacing-xs: 0.25rem;   /* 4px */
  --spacing-sm: 0.5rem;    /* 8px */
  --spacing-md: 1rem;      /* 16px */
  --spacing-lg: 1.5rem;    /* 24px */
  --spacing-xl: 2rem;      /* 32px */

  /* Border Radii */
  --radius-sm: 0.25rem;    /* 4px */
  --radius-md: 0.375rem;   /* 6px */
  --radius-lg: 0.5rem;     /* 8px */
  --radius-full: 9999px;   /* Pills & Badges */

  /* Elevation Shadows */
  --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
}
```

---

## 3. Typography

- **Font Family**: `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`
- **Headings**:
  - `h1`: `1.5rem` (24px), font-weight `600` / `700`, line-height `1.25`
  - `h2`: `1.125rem` (18px), font-weight `600`
  - `h3`: `1rem` (16px), font-weight `600`
- **Body**: `1rem` (16px), line-height `1.5`, color `--color-text`
- **Captions & Meta**: `0.875rem` (14px) and `0.75rem` (12px), color `--color-text-muted`

---

## 4. Component Styles

### 4.1 Buttons (`.btn`)
- `.btn`: Flexbox container, padding `var(--spacing-sm) var(--spacing-md)`, border-radius `var(--radius-md)`, transition `all 0.2s`.
- `.btn-primary`: Background `--color-primary`, text `#ffffff`, hover background `--color-primary-hover`.
- `.btn-outline`: Background `transparent`, border `1px solid var(--color-border)`, hover background `var(--color-background)`.

### 4.2 Status Badges (`.badge`)
- `.badge`: Inline-flex, gap `var(--spacing-xs)`, font-size `0.75rem`, font-weight `500`, border-radius `--radius-full`, padding `var(--spacing-xs) var(--spacing-sm)`.
- `.badge-pending`: Background `#fef3c7`, text `#92400e` (Amber).
- `.badge-running`: Background `#dbeafe`, text `#1e40af` (Blue).
- `.badge-completed`: Background `#d1fae5`, text `#065f46` (Green).
- `.badge-failed`: Background `#fee2e2`, text `#991b1b` (Red).

### 4.3 Data Tables (`.table`)
- Clean full-width table layout with `--color-border` bottom divider, light grey header background, and hover background highlight on table rows.

### 4.4 Form Controls (`.input`, `.label`)
- `.label`: Display block, font-size `0.875rem`, font-weight `500`, bottom margin `var(--spacing-xs)`.
- `.input`: Full width, padding `var(--spacing-sm) var(--spacing-md)`, border `1px solid var(--color-border)`, focus outline `2px solid var(--color-primary)`.
