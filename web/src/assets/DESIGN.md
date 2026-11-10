---
name: Neo-Industrial Finance
colors:
  surface: '#0b1326'
  surface-dim: '#0b1326'
  surface-bright: '#31394d'
  surface-container-lowest: '#060e20'
  surface-container-low: '#131b2e'
  surface-container: '#171f33'
  surface-container-high: '#222a3d'
  surface-container-highest: '#2d3449'
  on-surface: '#dae2fd'
  on-surface-variant: '#bbc9cd'
  inverse-surface: '#dae2fd'
  inverse-on-surface: '#283044'
  outline: '#859397'
  outline-variant: '#3c494c'
  surface-tint: '#2fd9f4'
  primary: '#8aebff'
  on-primary: '#00363e'
  primary-container: '#22d3ee'
  on-primary-container: '#005763'
  inverse-primary: '#006877'
  secondary: '#a4d64c'
  on-secondary: '#233600'
  secondary-container: '#719e13'
  on-secondary-container: '#1e2f00'
  tertiary: '#cddef8'
  on-tertiary: '#213145'
  tertiary-container: '#b2c2dc'
  on-tertiary-container: '#405065'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#a2eeff'
  primary-fixed-dim: '#2fd9f4'
  on-primary-fixed: '#001f25'
  on-primary-fixed-variant: '#004e5a'
  secondary-fixed: '#bff365'
  secondary-fixed-dim: '#a4d64c'
  on-secondary-fixed: '#131f00'
  on-secondary-fixed-variant: '#354e00'
  tertiary-fixed: '#d3e4fe'
  tertiary-fixed-dim: '#b7c8e1'
  on-tertiary-fixed: '#0b1c30'
  on-tertiary-fixed-variant: '#38485d'
  background: '#0b1326'
  on-background: '#dae2fd'
  surface-variant: '#2d3449'
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  data-display-lg:
    fontFamily: JetBrains Mono
    fontSize: 32px
    fontWeight: '500'
    lineHeight: 40px
    letterSpacing: -0.04em
  data-display-sm:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
  label-caps:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.1em
spacing:
  unit: 4px
  gutter: 16px
  margin-mobile: 16px
  margin-desktop: 40px
  container-max: 1440px
---

## Brand & Style

This design system is built for a fintech environment that prioritizes technical precision and high-speed data visualization. The personality is "Engineered Confidence"—it treats financial management like a high-performance terminal. The aesthetic merges **Neo-Industrial** functionalism with **Glassmorphism**, creating a high-contrast environment where critical data points cut through a deep, atmospheric backdrop. 

The target audience consists of power users and tech-forward individuals who view their finances as a system to be optimized. The UI should evoke a sense of being "in the cockpit," utilizing technical overlays, sharp geometry, and vibrant accent glows to signify real-time movement and liquidity.

## Colors

The palette is anchored in a deep slate "Ink" (#0f172a) to provide maximum contrast for functional accents.

- **Primary (Electric Cyan):** Used for primary actions, growth indicators, and active selection states.
- **Secondary (Neon Lime):** Reserved for "Success" states, profits, and secondary highlights that require immediate peripheral attention.
- **Surface Tiers:** Use a layering system of #1e293b (Surface) and #334155 (Overlay) to create structural hierarchy.
- **Functional Gradients:** Use 20% opacity washes of Electric Cyan for chart areas and glass backgrounds to maintain legibility while injecting color.

## Typography

This design system utilizes a dual-font strategy to separate UI navigation from financial data. 

**Inter** handles all interface copy, headers, and descriptions, providing a clean, neutral foundation. **JetBrains Mono** is strictly reserved for "The Numbers"—account balances, stock tickers, transaction amounts, and timestamps. This distinction allows users to scan for quantitative data instantly. 

All labels in JetBrains Mono should be set in Uppercase with slight tracking (letter-spacing) to mimic industrial identification tags.

## Layout & Spacing

The layout follows a rigorous 4px baseline grid. On desktop, use a 12-column fluid grid with 16px gutters. For mobile, a 4-column grid is standard.

A "Modular Block" philosophy is applied here: every component should feel like a standalone piece of hardware plugged into the dashboard. Use generous internal padding (24px) for cards to maintain a premium, airy feel despite the dark color palette. Sidebars are fixed width (280px) on desktop to provide a consistent "Command Center" anchor.

## Elevation & Depth

Depth is communicated through transparency and material physics rather than traditional fuzzy shadows.

- **The Sidebar:** Features a high-performance backdrop blur (32px) with a semi-transparent fill of the primary background color at 70% opacity.
- **Glass Borders:** Instead of shadows, use 1px inner borders (strokes). On elevated cards, use a top-down linear gradient stroke (White at 15% to White at 5%) to simulate a "rim light" hitting the edge of a glass pane.
- **Active State Glow:** When an element is focused or active, apply a subtle outer glow using the Primary color with a 20px blur at 30% opacity to simulate light emission.

## Shapes

The design system adopts a **Sharp (0px)** corner philosophy to reinforce the industrial, technical nature of the product. This creates a high-density, professional look where every pixel feels intentional. 

The only exception to the sharp rule is for internal "pill" indicators (status chips) which use a full radius to provide a visual break from the structural grid.

## Components

- **Buttons:** Primary buttons are sharp-edged blocks of Electric Cyan with black text. Secondary buttons are ghost-style with a 1px Cyan border.
- **Data Cards:** Use a dark surface (#1e293b) with a subtle grain texture overlay (2% opacity) to add a tactile, hardware feel.
- **Inputs:** Underline-only style or fully enclosed boxes with #334155 borders. The border should turn Electric Cyan on focus.
- **Status Chips:** Small, fully rounded capsules. Use Neon Lime for "Completed" or "Profitable" and a muted Slate for "Pending."
- **Visualizers:** Sparklines and progress bars should use high-saturation gradients (Cyan to Blue) with no smoothing, emphasizing the raw data points.
- **Terminal Feed:** A specialized list component using JetBrains Mono for transaction history, styled to look like a scrolling system log.