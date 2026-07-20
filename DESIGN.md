---
name: VocalKart
description: AI-powered voice ordering platform for Indian retail
colors:
  surface-deep: "#030712"
  surface-mid: "#171717"
  surface-elevated: "#1c1c1c"
  border-subtle: "#262626"
  text-primary: "#ffffff"
  text-secondary: "#a3a3a3"
  text-muted: "#737373"
  accent-blue: "#60a5fa"
  accent-purple: "#c084fc"
  accent-pink: "#f472b6"
  cta-primary: "#2563eb"
  cta-hover: "#1d4ed8"
  success: "#22c55e"
  destructive: "#ef4444"
typography:
  display:
    fontFamily: "Inter Variable, sans-serif"
    fontSize: "clamp(2.5rem, 5vw, 4.5rem)"
    fontWeight: 800
    lineHeight: 1
    letterSpacing: "normal"
  body:
    fontFamily: "Inter Variable, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "Inter Variable, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 500
    letterSpacing: "0.05em"
    textTransform: "uppercase"
rounded:
  sm: "0.5rem"
  md: "0.625rem"
  lg: "0.75rem"
  xl: "1rem"
  xxl: "1.5rem"
  full: "9999px"
spacing:
  xs: "0.25rem"
  sm: "0.5rem"
  md: "1rem"
  lg: "1.5rem"
  xl: "2rem"
  xxl: "4rem"
components:
  button-primary:
    backgroundColor: "{colors.cta-primary}"
    textColor: "{colors.text-primary}"
    rounded: "{rounded.xl}"
    padding: "1rem 2rem"
    fontSize: "1.125rem"
    fontWeight: 600
  button-primary-hover:
    backgroundColor: "{colors.cta-hover}"
    textColor: "{colors.text-primary}"
  button-ghost:
    backgroundColor: transparent
    textColor: "{colors.text-secondary}"
    rounded: "{rounded.lg}"
    padding: "0.5rem 1rem"
  card-default:
    backgroundColor: "{colors.surface-mid}"
    rounded: "{rounded.xxl}"
    border: "1px solid {colors.border-subtle}"
  card-hover:
    border: "1px solid {colors.accent-blue}"
  input:
    backgroundColor: transparent
    rounded: "{rounded.lg}"
    border: "1px solid {colors.border-subtle}"
    textColor: "{colors.text-primary}"
  nav-link:
    textColor: "{colors.text-secondary}"
    fontWeight: 500
  nav-link-active:
    textColor: "{colors.text-primary}"
  badge:
    backgroundColor: "rgba(37, 99, 235, 0.1)"
    border: "1px solid rgba(59, 130, 246, 0.2)"
    textColor: "{colors.accent-blue}"
    rounded: "{rounded.full}"
---

# Design System: VocalKart

## 1. Overview

**Creative North Star: "The Bazaar Voice"**

VocalKart's visual language is the digital embodiment of a trusted Indian bazaar — bold presence, warm familiarity, and the quiet confidence of a shopkeeper who knows your name. The system operates entirely in dark mode, with deep charcoal surfaces that recede to let the conversational AI take center stage. Color is used sparingly and strategically: a blue-purple-pink gradient family signals the product's bilingual, tech-forward nature without overwhelming.

This system explicitly rejects the generic SaaS template — no white cards on gray backgrounds, no Inter-heavy typography as default, no bounce easings or glassmorphism for decoration. The interface should feel like it belongs to Indian retail: direct, warm, and efficient.

**Key Characteristics:**
- Dark-first: neutral-950 base with tonal layering for depth
- Gradient accent family (blue → purple → pink) as a unified brand system, not decoration
- Flat surfaces with glow accents — orbs and blurred backdrops for atmosphere, never shadows for elevation
- Generous rounded corners (1rem–1.5rem) for approachability
- Motion is purposeful and restrained: ease-out-quart curves, no bounce or elastic

## 2. Colors

Dark-mode only. The palette is built around deep neutrals with a blue-purple-pink accent family used as a cohesive brand gradient system.

### Primary
- **VocalKart Blue** (`#2563eb` → `#1d4ed8` hover): The primary call-to-action. Used on the main button, interactive badges, and link hover states. Conveys trust without being cold.

### Accent Family (Gradient System)
- **Accent Blue** (`#60a5fa`): The cool pole of the brand gradient. Used inline for keyword emphasis ("Hindi", "English").
- **Accent Purple** (`#c084fc`): The mid point. Used in the scroll progress bar, step connectors, and icon backgrounds.
- **Accent Pink** (`#f472b6`): The warm pole. Used in testimonial labels and gradient tails.

### Neutral
- **Surface Deep** (`#030712` / neutral-950): Primary page background. Anchors the entire experience.
- **Surface Mid** (`#171717` / neutral-900 @ 40–60% opacity): Cards, accordions, and elevated panels.
- **Surface Elevated** (`#1c1c1c`): The tap-target hover state for interactive cards.
- **Border Subtle** (`#262626` / neutral-800 @ 50–70% opacity): Separators, card outlines, and input strokes.
- **Text Primary** (`#ffffff`): Headings, primary body copy, and button labels.
- **Text Secondary** (`#a3a3a3` / neutral-400): Body text, descriptive paragraphs, and supporting copy.
- **Text Muted** (`#737373` / neutral-500): Microcopy, timestamps, footer text.

### Named Rules
**The Gradient-As-Brand Rule.** The blue‑purple‑pink gradient is not decoration — it is the brand's chromatic signature. It appears in the hero heading, the scroll progress bar, step connectors, and button hover glows. Never break the gradient into isolated single stops outside the accent family.

**The Neutral Dominance Rule.** 90% of any given screen is deep neutrals. Color is a rare resource: badges, gradient text, and the primary CTA carry the entire emotional load. When everything is colorful, nothing is.

## 3. Typography

**Display & Body Font:** Inter Variable (sans-serif)

**Character:** Inter's wide glyph set and variable axes give stability across Hindi and English text in the same viewport. The same typeface handles both, avoiding awkward pairings. Weight contrast (800 for display vs 400 for body) creates hierarchy without a second family.

### Hierarchy
- **Display** (ExtraBold 800, `clamp(2.5rem, 5vw, 4.5rem)`, line-height 1): Hero headlines only. Always `text-wrap: balance`. Gradient text in the brand accent family.
- **Headline** (Bold 700, `clamp(1.5rem, 3vw, 2.25rem)`, line-height 1.2): Section titles. Solid white.
- **Title** (Semibold 600, `1rem`–`1.125rem`, line-height 1.3): Card headings, feature names, FAQ questions.
- **Body** (Regular 400, `0.875rem`–`1rem`, line-height 1.6): Paragraphs and descriptions. `text-neutral-400`. Max width 65ch for readability.
- **Label** (Medium 500, `0.75rem`, letter-spacing `0.05em`, uppercase): Section kickers, badge text, metric labels. Always uppercase, tracked wide. Used once per section only.

### Named Rules
**The One-Family Rule.** Inter Variable handles display, body, and label roles. No second typeface. Hierarchy is achieved through weight, size, and color, not a font swap.

## 4. Elevation

The system is flat by default. Depth is created through tonal layering (darker background → lighter card surface) and atmospheric glow, not drop shadows. Glow orbs (`blur-3xl` with low-opacity brand colors) sit behind key sections to create a sense of ambient light. Cards lift on hover via `translateY(-3px)` with a border color shift to the accent family, but never cast a shadow.

This approach keeps the interface feeling physical and warm without the corporate weight of box shadows.

## 5. Components

### Buttons
- **Shape:** Generously rounded corners (1rem / 16px).
- **Primary ("Call Me Now"):** `bg-blue-600` on `surface-deep`, white bold text, full-width on mobile. Hover shifts to `bg-blue-700` with a matching glow (`shadow-lg shadow-blue-600/25`). Loading state rotates the phone icon.
- **Ghost / Nav:** Transparent background, secondary text color. Hover fades to white. No border, no lift.
- **Secondary (Get Started):** Same shape as primary but used inline in nav bars. Consistent visual weight.

### Cards / Containers
- **Corner Style:** 1.5rem (24px) radius.
- **Background:** `bg-neutral-900/40` to `bg-neutral-900/60` (translucent, layered over the deep background).
- **Border:** Subtle `border-neutral-800/60` at rest, shifts to `border-blue-500/30` on hover.
- **Shadow Strategy:** None. Depth from tonal contrast + backdrop blur (`backdrop-blur-sm`).
- **Hover:** Lifts 3–4px with a border color shift and subtle scale (1.01).

### Inputs / Fields
- **Phone Input:** The main interaction point on the hero. Uses `react-phone-number-input` with default country India. Clean transparent background on the dark surface. Error state in red (`text-red-500`).
- **Focus Treatment:** Border shift to accent, no glow ring.

### Navigation
- **Style:** Fixed top bar, `backdrop-blur-xl` with `bg-neutral-950/70` for translucency. Neutral-400 link text, white on hover. Gradient brand logo text.
- **Mobile:** Slide-down accordion drawer with stacked full-width links and CTA.

### Badges / Pills
- **Shape:** Full rounded.
- **Style:** `bg-blue-600/10` background, `border-blue-500/20`, `text-blue-400`. Backdrop blur. Inline icon (`Zap`) for "AI-Powered" labels.

### Testimonial Carousel
- **Card:** Same card pattern with a gradient avatar circle (blue → purple) and star ratings in yellow. Auto-rotates every 5s with horizontal slide animation.

### FAQ Accordion
- **Trigger:** Full-width card-style header with plus/chevron icon rotated on open. Slide animation for content reveal.
- **Shape:** Rounded-xl (0.75rem).

## 6. Do's and Don'ts

### Do:
- **Do** use the blue-purple-pink gradient as the single brand chromatic signature — in the hero heading, scroll bar, and step connectors.
- **Do** keep 90% of surfaces in deep neutral tones. Color is accent, not atmosphere.
- **Do** use motion purposefully: ease-out curves, scroll-triggered reveals, hover lifts. Every animation should answer "what state changed?"
- **Do** use large corner radii (1rem–1.5rem) on interactive containers for approachability.
- **Do** test every heading at mobile widths — clamp scales plus long Hindi/English words overflow easily.

### Don't:
- **Don't** use drop shadows. Depth comes from tonal layering and backdrop blur.
- **Don't** use bounce, elastic, or spring easings on any animation. Stick to ease-out-quart / ease-out-quint.
- **Don't** wrap content in nested cards. One layer of containment per section.
- **Don't** use side-stripe borders (border-left/right > 1px as accent).
- **Don't** use glassmorphism (backdrop blur with semi-transparent backgrounds and bright borders) as a default container style. Blur is reserved for the nav bar and hero glow orbs.
- **Don't** add numbered section markers (01, 02, 03) above every section header. Numbers earn their place only when the content is a real sequence.
- **Don't** use gray text on colored backgrounds. Text on colored surfaces should use a tint of the surface's own hue or a transparency of the text color.
