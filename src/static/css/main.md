---
name: Deep Industrial Minimalist
colors:
  surface: '#0c1322'
  surface-dim: '#0c1322'
  surface-bright: '#323949'
  surface-container-lowest: '#070e1d'
  surface-container-low: '#141b2b'
  surface-container: '#191f2f'
  surface-container-high: '#232a3a'
  surface-container-highest: '#2e3545'
  on-surface: '#dce2f7'
  on-surface-variant: '#d8c3ad'
  inverse-surface: '#dce2f7'
  inverse-on-surface: '#293040'
  outline: '#a08e7a'
  outline-variant: '#534434'
  surface-tint: '#ffb95f'
  primary: '#ffc174'
  on-primary: '#472a00'
  primary-container: '#f59e0b'
  on-primary-container: '#613b00'
  inverse-primary: '#855300'
  secondary: '#4edea3'
  on-secondary: '#003824'
  secondary-container: '#00a572'
  on-secondary-container: '#00311f'
  tertiary: '#c2cce0'
  on-tertiary: '#273140'
  tertiary-container: '#a7b1c4'
  on-tertiary-container: '#3a4454'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffddb8'
  primary-fixed-dim: '#ffb95f'
  on-primary-fixed: '#2a1700'
  on-primary-fixed-variant: '#653e00'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#d9e3f7'
  tertiary-fixed-dim: '#bdc7db'
  on-tertiary-fixed: '#121c2a'
  on-tertiary-fixed-variant: '#3d4757'
  background: '#0c1322'
  on-background: '#dce2f7'
  surface-variant: '#2e3545'
typography:
  display-lg:
    fontFamily: Geist
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Geist
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  data-mono:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-caps:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  sidebar_width: 240px
  gutter: 12px
  container_padding: 16px
  stack_sm: 8px
  stack_md: 16px
  stack_lg: 24px
---

## Brand & Style
The design system is engineered for operational precision and high-stakes decision-making. It adopts a **Deep Industrial Minimalist** aesthetic, prioritizing data density and cognitive efficiency over decorative elements. The system is designed to evoke a sense of professional authority, reliability, and technical sophistication.

Drawing from **Modern Corporate Utility** and **Structural Minimalism**, the UI utilizes a high-contrast dark environment to reduce eye strain during long operational shifts while highlighting critical action paths with surgical precision. Every element exists to serve a functional purpose; whitespace is used not just for aesthetics, but as a structural tool to separate complex data streams.

## Colors
This design system utilizes a high-contrast palette optimized for dark-mode environments, with a secondary light-mode implementation for high-glare environments.

- **Primary (Amber Orange):** Reserved strictly for primary actions, critical state changes, and interactive sequence controls.
- **Secondary (Emerald Green):** Used exclusively for "optimized" states, success metrics, and positive delta indicators in fleet performance.
- **Tertiary (Slate Gray):** Provides the structural scaffolding for cards, dividers, and secondary button backgrounds.
- **Base (Charcoal Black):** The foundation of the workspace, providing a non-reflective, deep surface that makes data "pop."
- **Status Tints:** Use 10% opacity versions of primary and secondary colors for large-area background highlights (e.g., row selection or path highlighting).

## Typography
The typographic hierarchy prioritizes legibility in data-dense environments. 

- **Geist** is used for headlines and UI headers, providing a technical, geometric rigour.
- **Inter** handles all body copy and standard UI labels to ensure maximum readability across varying screen resolutions.
- **JetBrains Mono** is employed for all numerical data, coordinates, timestamps, and sequence IDs. This ensures that columns of numbers align vertically (tabular lining) for easier scanning and comparison.
- **Scale:** Maintain a tight scale. In utility tools, information density is a feature. Do not use excessive font sizes for desktop views.

## Layout & Spacing
The layout follows a **Rigid Grid** philosophy. It uses a 4px baseline grid to ensure all components align precisely, reflecting the industrial nature of the tool.

- **Grid:** 12-column desktop grid with a fixed 240px left sidebar for global navigation. 
- **Density:** Use "Compact" spacing for tables and data lists (8px cell padding).
- **Split-Screen:** For optimization workflows, use a 50/50 or 60/40 vertical split, allowing users to adjust parameters on the left while viewing sequence changes on the right.
- **Breakpoints:** 
  - Mobile (<768px): Sidebar collapses to a bottom bar or hamburger; grid becomes 1-column.
  - Tablet (768px - 1280px): Sidebar collapses to icon-only rail.
  - Desktop (>1280px): Fixed sidebar, fluid content area.

## Elevation & Depth
In this design system, depth is communicated through **Tonal Layering** and **Structural Outlines** rather than soft shadows.

- **Level 0 (Surface):** Charcoal Black (#111827). Used for the global background.
- **Level 1 (Card/Container):** Slate Gray (#1F2937 - a shade lighter than base). Used for data cards and sidebar.
- **Level 2 (Inlay/Input):** Deep Black (#030712). Used for input fields and text areas to create an "inset" feel.
- **Borders:** Use 1px solid borders (#374151) to define edges. Avoid dropshadows entirely to maintain a crisp, digital-industrial look. 
- **Active State:** Use the Primary Amber Orange as a 2px left-border accent to indicate active selection in lists or navigation.

## Shapes
The shape language is **Soft-Industrial**. 

- **Corner Radius:** All standard components (cards, buttons, inputs) use a 4px (0.25rem) radius. This provides a subtle nod to modern hardware design without losing the professional, "engineered" feel of sharp corners.
- **Interactive Elements:** Buttons and tags maintain the same 4px radius. 
- **KPI Metrics:** Large numerical displays should be uncontained (no background) or placed in a strictly rectangular container to emphasize the data.

## Components
- **Buttons:** 
  - *Primary:* Amber Orange background, Black text, Bold weight. High visibility.
  - *Secondary:* Transparent background, 1px Slate Gray border, White text.
- **Data Cards:** Slate Gray background, 1px border (#4B5563), 16px internal padding. Title in `label-caps`.
- **KPI Metrics:** Large `display-lg` numbers in White or Emerald Green (if positive), paired with a `label-caps` descriptor.
- **Data Tables:** Zebra-striping is discouraged. Use 1px horizontal dividers only. High-density row height (32px). Use `data-mono` for all numeric cells.
- **Slider Controllers:** Amber Orange track for the active portion, Slate Gray for the remaining track. Knobs should be square or slightly rounded (4px) white blocks for tactile contrast.
- **Status Chips:** Small, condensed pills with 10% opacity background of the status color (Green for Optimized, Amber for Warning, Red for Error) and 100% opacity text.
- **Sidebar:** Narrow, dark-themed, using icon + label. Active state indicated by Amber Orange vertical line on the leading edge.