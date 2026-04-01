# GSTSaathi Design System & Style Guide

**Version:** 1.0.0  
**Last Updated:** April 2026  
**Framework:** React 18 + Ant Design 5 + Vite

---

## Table of Contents

1. [Design Principles](#design-principles)
2. [Color Palette](#color-palette)
3. [Typography](#typography)
4. [Spacing & Layout](#spacing--layout)
5. [Components](#components)
6. [Icons](#icons)
7. [Imagery & Graphics](#imagery--graphics)
8. [Motion & Animation](#motion--animation)
9. [Accessibility](#accessibility)
10. [Responsive Design](#responsive-design)
11. [Dark Mode](#dark-mode)

---

## Design Principles

### 1. Trust & Professionalism
GSTSaathi handles sensitive financial data. The design must convey reliability, security, and competence.

### 2. Clarity Over Creativity
Users need to quickly understand compliance status, mismatches, and actions required. Prioritize readability and scannability.

### 3. Efficiency
Minimize clicks. Surface important information prominently. Enable quick actions from anywhere.

### 4. Consistency
Use consistent patterns, spacing, colors, and interactions throughout the application.

### 5. Accessibility
Design for all users, including those with visual impairments. Meet WCAG 2.1 AA standards.

---

## Color Palette

### Primary Colors

| Name | Token | Hex | Usage |
|------|-------|-----|-------|
| **Daybreak Blue** | `--color-primary` | `#1677ff` | Primary actions, links, active states, branding |
| **Daybreak Blue Hover** | `--color-primary-hover` | `#4096ff` | Hover states |
| **Daybreak Blue Active** | `--color-primary-active` | `#0958d9` | Active/clicked states |
| **Geek Blue** | `--color-secondary` | `#2f54eb` | Secondary actions, accents |

### Functional Colors

| Name | Token | Hex | Usage |
|------|-------|-----|-------|
| **Polar Green** | `--color-success` | `#52c41a` | Success states, ITC available, compliant items |
| **Sunset Orange** | `--color-warning` | `#fa8c16` | Warnings, ITC at risk, pending actions |
| **Dust Red** | `--color-error` | `#ff4d4f` | Errors, validation failures, critical issues |
| **Cyan** | `--color-info` | `#13c2c2` | Informational messages, tips |

### Neutral Colors

| Name | Token | Hex | Usage |
|------|-------|-----|-------|
| **Gray-0** | `--color-gray-0` | `#ffffff` | Backgrounds, cards |
| **Gray-1** | `--color-gray-1` | `#fafafa` | Alternate backgrounds |
| **Gray-2** | `--color-gray-2` | `#f5f5f5` | Section backgrounds |
| **Gray-3** | `--color-gray-3` | `#f0f0f0` | Borders, dividers |
| **Gray-4** | `--color-gray-4` | `#d9d9d9` | Disabled states |
| **Gray-5** | `--color-gray-5` | `#bfbfbf` | Placeholder text |
| **Gray-6** | `--color-gray-6` | `#8c8c8c` | Secondary text |
| **Gray-7** | `--color-gray-7` | `#595959` | Body text |
| **Gray-8** | `--color-gray-8` | `#262626` | Headings |
| **Gray-9** | `--color-gray-9` | `#000000` | Primary text |

### Data Visualization Colors

| Name | Hex | Usage |
|------|-----|-------|
| **Blue** | `#1677ff` | Primary data series |
| **Green** | `#52c41a` | Positive values, growth |
| **Orange** | `#fa8c16` | Caution, moderate values |
| **Red** | `#ff4d4f` | Negative values, decline |
| **Purple** | `#722ed1` | Secondary data series |
| **Cyan** | `#13c2c2` | Tertiary data series |
| **Gold** | `#faad14` | Highlights, special metrics |

### Gradient Presets

```css
/* Primary Gradient */
background: linear-gradient(135deg, #1677ff 0%, #2f54eb 100%);

/* Success Gradient */
background: linear-gradient(135deg, #52c41a 0%, #73d13d 100%);

/* Warning Gradient */
background: linear-gradient(135deg, #fa8c16 0%, #ffc069 100%);

/* Hero Background */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

---

## Typography

### Font Family

```css
--font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 
               'Helvetica Neue', Arial, 'Noto Sans', sans-serif,
               'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol';

--font-family-mono: 'SF Mono', 'Fira Code', 'Fira Mono', 
                    'Roboto Mono', monospace;
```

### Font Sizes

| Name | Token | Size (px) | Line Height | Usage |
|------|-------|-----------|-------------|-------|
| **XS** | `--font-size-xs` | 12 | 1.5 | Captions, footnotes |
| **SM** | `--font-size-sm` | 14 | 1.57 | Secondary text, labels |
| **MD** | `--font-size-md` | 16 | 1.5 | Body text |
| **LG** | `--font-size-lg` | 20 | 1.4 | Lead paragraphs |
| **XL** | `--font-size-xl` | 24 | 1.35 | H4 headings |
| **2XL** | `--font-size-2xl` | 30 | 1.3 | H3 headings |
| **3XL** | `--font-size-3xl` | 38 | 1.25 | H2 headings |
| **4XL** | `--font-size-4xl` | 46 | 1.2 | H1 headings |

### Font Weights

| Name | Token | Value | Usage |
|------|-------|-------|-------|
| **Regular** | `--font-weight-regular` | 400 | Body text |
| **Medium** | `--font-weight-medium` | 500 | Labels, buttons |
| **Semibold** | `--font-weight-semibold` | 600 | Subheadings |
| **Bold** | `--font-weight-bold` | 700 | Headings, emphasis |

### Text Styles

```css
/* Heading 1 */
font-size: 46px;
font-weight: 700;
line-height: 1.2;
color: #262626;

/* Heading 2 */
font-size: 38px;
font-weight: 600;
line-height: 1.25;
color: #262626;

/* Heading 3 */
font-size: 30px;
font-weight: 600;
line-height: 1.3;
color: #262626;

/* Heading 4 */
font-size: 24px;
font-weight: 600;
line-height: 1.35;
color: #262626;

/* Body Large */
font-size: 20px;
font-weight: 400;
line-height: 1.4;
color: #595959;

/* Body */
font-size: 16px;
font-weight: 400;
line-height: 1.5;
color: #595959;

/* Body Small */
font-size: 14px;
font-weight: 400;
line-height: 1.57;
color: #8c8c8c;

/* Caption */
font-size: 12px;
font-weight: 400;
line-height: 1.5;
color: #8c8c8c;
```

---

## Spacing & Layout

### Spacing Scale (8px Grid)

| Name | Token | Value (px) | Usage |
|------|-------|------------|-------|
| **XS** | `--spacing-xs` | 4 | Tight spacing, icon gaps |
| **SM** | `--spacing-sm` | 8 | Small gaps, form fields |
| **MD** | `--spacing-md` | 16 | Standard padding, margins |
| **LG** | `--spacing-lg` | 24 | Section spacing |
| **XL** | `--spacing-xl` | 32 | Large section gaps |
| **2XL** | `--spacing-2xl` | 48 | Page sections |
| **3XL** | `--spacing-3xl` | 64 | Major divisions |

### Layout Containers

| Breakpoint | Max Width | Padding |
|------------|-----------|---------|
| **Mobile** | 100% | 16px |
| **Tablet** | 768px | 24px |
| **Desktop** | 1024px | 32px |
| **Large** | 1440px | 48px |
| **XL** | 1920px | 64px |

### Grid System

- **Columns:** 12-column grid
- **Gutters:** 16px (mobile), 24px (tablet+), 32px (desktop)
- **Margins:** 16px (mobile), 24px (tablet+), 32px (desktop)

### Common Layout Patterns

```
┌─────────────────────────────────────┐
│           Header (64px)             │
├─────────┬───────────────────────────┤
│         │                           │
│ Sidebar │      Main Content         │
│ (256px) │      (flex-1)             │
│         │                           │
└─────────┴───────────────────────────┘
```

---

## Components

### Buttons

#### Primary Button
```css
background: #1677ff;
color: #ffffff;
padding: 8px 16px;
border-radius: 6px;
font-size: 14px;
font-weight: 500;
height: 32px;
```

#### Secondary Button
```css
background: #ffffff;
color: #595959;
border: 1px solid #d9d9d9;
padding: 8px 16px;
border-radius: 6px;
font-size: 14px;
font-weight: 500;
height: 32px;
```

#### Button Sizes
| Size | Height | Padding | Font Size |
|------|--------|---------|-----------|
| Small | 24px | 4px 8px | 12px |
| Medium | 32px | 8px 16px | 14px |
| Large | 40px | 12px 24px | 16px |

### Cards

```css
background: #ffffff;
border: 1px solid #f0f0f0;
border-radius: 8px;
padding: 24px;
box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.03),
            0 1px 6px -1px rgba(0, 0, 0, 0.02),
            0 2px 4px 0 rgba(0, 0, 0, 0.02);
```

### Input Fields

```css
background: #ffffff;
border: 1px solid #d9d9d9;
border-radius: 6px;
padding: 8px 12px;
height: 32px;
font-size: 14px;
transition: all 0.2s;
```

**Focus State:**
```css
border-color: #4096ff;
box-shadow: 0 0 0 2px rgba(22, 119, 255, 0.2);
```

**Error State:**
```css
border-color: #ff4d4f;
```

### Tables

```css
/* Header */
background: #fafafa;
font-weight: 600;
font-size: 14px;
color: #262626;

/* Row */
background: #ffffff;
border-bottom: 1px solid #f0f0f0;

/* Hover */
background: #fafafa;

/* Striped */
:nth-child(even) { background: #fafafa; }
```

### Badges

| Status | Background | Text Color |
|--------|------------|------------|
| Success | `#f6ffed` | `#52c41a` |
| Warning | `#fff7e6` | `#fa8c16` |
| Error | `#fff1f0` | `#ff4d4f` |
| Info | `#e6fffb` | `#13c2c2` |
| Default | `#f5f5f5` | `#595959` |

### Stat Cards

```css
/* Container */
background: #ffffff;
border: 1px solid #f0f0f0;
border-radius: 8px;
padding: 24px;

/* Title */
font-size: 14px;
color: #8c8c8c;
margin-bottom: 8px;

/* Value */
font-size: 30px;
font-weight: 600;
color: #262626;

/* Trend */
font-size: 12px;
font-weight: 500;
```

---

## Icons

### Icon Library
**Primary:** Ant Design Icons (`@ant-design/icons`)

### Icon Sizes
| Size | Token | Value (px) |
|------|-------|------------|
| XS | `--icon-xs` | 12 |
| SM | `--icon-sm` | 16 |
| MD | `--icon-md` | 20 |
| LG | `--icon-lg` | 24 |
| XL | `--icon-xl` | 32 |

### Icon Usage Guidelines
- Always pair icons with text labels for clarity
- Use consistent stroke weight (2px)
- Maintain 2px padding around icons
- Use color semantically (green for success, red for errors)

### Common Icons
| Purpose | Icon Name |
|---------|-----------|
| Dashboard | `DashboardOutlined` |
| Upload | `UploadOutlined` |
| Reconcile | `SyncOutlined` |
| Export | `ExportOutlined` |
| Settings | `SettingOutlined` |
| Success | `CheckCircleOutlined` |
| Warning | `WarningOutlined` |
| Error | `CloseCircleOutlined` |
| Info | `InfoCircleOutlined` |

---

## Imagery & Graphics

### Logo
- **Format:** SVG (preferred) or PNG
- **Sizes:** 32px, 48px, 64px
- **Clear Space:** Minimum 8px on all sides

### Illustrations
- Use for empty states, onboarding, and error pages
- Style: Clean, minimal, professional
- Colors: Match brand palette
- Avoid: Cartoony or overly playful styles

### Charts & Graphs
- Use data visualization colors
- Maintain sufficient contrast
- Include clear labels and legends
- Provide alternative text for accessibility

---

## Motion & Animation

### Duration

| Name | Token | Value (ms) | Usage |
|------|-------|------------|-------|
| **Instant** | `--duration-instant` | 0 | No animation |
| **Fast** | `--duration-fast` | 150 | Micro-interactions |
| **Normal** | `--duration-normal` | 250 | Standard transitions |
| **Slow** | `--duration-slow` | 350 | Complex animations |
| **Slower** | `--duration-slower` | 500 | Large elements |

### Easing

```css
--ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);
--ease-out: cubic-bezier(0, 0, 0.58, 1);
--ease-in: cubic-bezier(0.42, 0, 1, 1);
--ease-bounce: cubic-bezier(0.68, -0.55, 0.265, 1.55);
```

### Common Animations

#### Fade In
```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

#### Slide Up
```css
@keyframes slideUp {
  from { 
    opacity: 0;
    transform: translateY(20px);
  }
  to { 
    opacity: 1;
    transform: translateY(0);
  }
}
```

#### Scale In
```css
@keyframes scaleIn {
  from { 
    opacity: 0;
    transform: scale(0.95);
  }
  to { 
    opacity: 1;
    transform: scale(1);
  }
}
```

### Animation Guidelines
- Keep animations under 400ms
- Use easing for natural motion
- Animate opacity and transform only (performance)
- Respect `prefers-reduced-motion` setting

---

## Accessibility

### Color Contrast
- **Normal Text:** Minimum 4.5:1 contrast ratio
- **Large Text (18px+):** Minimum 3:1 contrast ratio
- **UI Components:** Minimum 3:1 contrast ratio

### Keyboard Navigation
- All interactive elements must be focusable
- Visible focus indicators (2px outline)
- Logical tab order
- Skip links for main content

### Screen Reader Support
- Semantic HTML elements
- ARIA labels where needed
- Alt text for images
- Descriptive link text

### Focus States
```css
:focus-visible {
  outline: 2px solid #1677ff;
  outline-offset: 2px;
}
```

### Common ARIA Patterns

```jsx
// Loading state
<div aria-live="polite" aria-busy="true">Loading...</div>

// Error message
<div role="alert" aria-live="assertive">Error message</div>

// Button with icon
<button aria-label="Upload file">
  <UploadIcon aria-hidden="true" />
</button>
```

---

## Responsive Design

### Breakpoints

| Name | Token | Min Width | Max Width | Target |
|------|-------|-----------|-----------|--------|
| **XS** | `--bp-xs` | 0 | 575px | Small phones |
| **SM** | `--bp-sm` | 576px | 767px | Large phones |
| **MD** | `--bp-md` | 768px | 991px | Tablets |
| **LG** | `--bp-lg` | 992px | 1199px | Laptops |
| **XL** | `--bp-xl` | 1200px | 1599px | Desktops |
| **2XL** | `--bp-2xl` | 1600px | ∞ | Large screens |

### Responsive Patterns

#### Mobile-First Media Queries
```css
/* Base styles (mobile) */
.container { padding: 16px; }

/* Tablet+ */
@media (min-width: 768px) {
  .container { padding: 24px; }
}

/* Desktop+ */
@media (min-width: 1200px) {
  .container { padding: 32px; max-width: 1440px; }
}
```

#### Responsive Grid
```css
/* Mobile: 1 column */
.grid { grid-template-columns: 1fr; }

/* Tablet: 2 columns */
@media (min-width: 768px) {
  .grid { grid-template-columns: repeat(2, 1fr); }
}

/* Desktop: 3-4 columns */
@media (min-width: 1200px) {
  .grid { grid-template-columns: repeat(3, 1fr); }
}
```

### Touch Targets
- **Minimum Size:** 44x44px
- **Recommended:** 48x48px
- **Spacing:** 8px between targets

---

## Dark Mode

### Dark Mode Colors

| Light Mode | Dark Mode | Usage |
|------------|-----------|-------|
| `#ffffff` | `#141414` | Background |
| `#fafafa` | `#1f1f1f` | Card background |
| `#f5f5f5` | `#262626` | Section background |
| `#000000` | `#ffffff` | Primary text |
| `#262626` | `#e6e6e6` | Headings |
| `#595959` | `#bfbfbf` | Body text |
| `#8c8c8c` | `#8c8c8c` | Secondary text |

### Dark Mode Implementation

```css
[data-theme='dark'] {
  --color-bg: #141414;
  --color-card: #1f1f1f;
  --color-text: #ffffff;
  --color-text-secondary: #bfbfbf;
  --color-border: #303030;
}
```

### Dark Mode Guidelines
- Reduce saturation of brand colors by 20%
- Increase elevation shadows for depth
- Test all components in both modes
- Use `prefers-color-scheme` for auto-detection

---

## Page-Specific Guidelines

### Dashboard
- **Hero Metrics:** Large stat cards at top
- **Charts:** Use for trends and comparisons
- **Quick Actions:** Prominent CTAs for common tasks
- **Alerts:** Surface urgent issues prominently

### Upload
- **Dropzone:** Large, clear, with visual feedback
- **Progress:** Show real-time upload status
- **Validation:** Inline error messages
- **History:** Recent uploads table

### Reconcile
- **Status:** Clear progress indicator
- **Results:** Sortable, filterable table
- **Actions:** Bulk operations available
- **Export:** One-click report download

### Export
- **Format Cards:** Clear visual distinction
- **Preview:** Show sample before download
- **Options:** Date range, filters

---

## Implementation Checklist

### Phase 1: Foundation
- [ ] Create theme configuration file
- [ ] Set up CSS custom properties
- [ ] Configure Ant Design theme
- [ ] Create typography styles
- [ ] Define spacing utilities

### Phase 2: Components
- [ ] Build StatCard component
- [ ] Build DataTable component
- [ ] Build StatusBadge component
- [ ] Build EmptyState component
- [ ] Build LoadingState component

### Phase 3: Layout
- [ ] Create sidebar navigation
- [ ] Implement responsive header
- [ ] Add breadcrumb component
- [ ] Create page layouts

### Phase 4: Pages
- [ ] Redesign Login page
- [ ] Redesign Dashboard page
- [ ] Redesign Upload page
- [ ] Redesign Reconcile page
- [ ] Redesign Export page
- [ ] Redesign Settings page

### Phase 5: Polish
- [ ] Add animations
- [ ] Implement dark mode
- [ ] Accessibility audit
- [ ] Performance optimization

---

## Resources

### Design Tools
- [Ant Design Theme Editor](https://ant.design/theme-en)
- [Figma](https://figma.com) - Design mockups
- [Coolors](https://coolors.co) - Color palette generation

### Development Tools
- [Ant Design Components](https://ant.design/components/overview)
- [Ant Design Icons](https://ant.design/components/icon)
- [Recharts](https://recharts.org) - Charts
- [Framer Motion](https://www.framer.com/motion) - Animations

### Accessibility
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [axe DevTools](https://www.deque.com/axe/devtools/)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | April 2026 | Initial design system |

---

*This design system is a living document. Update it as the product evolves.*
