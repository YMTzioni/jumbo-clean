# DESIGN.md — ג׳מבו קלין v5

> אתר של בעל מקצוע שעובד טוב: תמונות של עבודה אמיתית, טיפוגרפיה צפופה ובטוחה, וברק אחד שזז – כמו רצפה אחרי פוליש.

## 1. Visual Theme & Atmosphere

**Header mark**: ג׳מבו קלין + slogan "מהשיפוץ ועד הברק" (replaced "+ שיפוצים").
**Style**: Warm Professional × Trade Editorial (seed 4 + brand navy/brass from the logo)
**Keywords**: עבודת שטח, ברק, אמינות, צפוף, חם, מודרני, ישראלי
**Tone**: בטוח, ענייני, קצת גאה — NOT luxury hotel, NOT stock-photo, NOT tech-startup glow
**Feel**: כמו להיכנס לדירה ביום מסירת המפתח – אבק אחרון באוויר והרצפה מחזירה את האור.

**Interaction Tier**: L2 (scene-defaults baseline for Landing Page)
**Dependencies**: CSS + vanilla JS (IntersectionObserver, rAF). No GSAP, no Lenis, no WebGL.

## 2. Color Palette & Roles

```css
:root {
  /* Backgrounds */
  --bg:            oklch(97.4% 0.006 85);   /* paper */
  --surface:       oklch(100% 0 0);         /* cards on paper */
  --surface-alt:   oklch(94% 0.012 82);     /* alternating section */
  --surface-hover: oklch(91% 0.016 80);
  --night:         oklch(18.5% 0.05 266);   /* hero / dark sections */
  --night-2:       oklch(25% 0.055 266);
  --night-3:       oklch(32% 0.05 266);

  /* Borders */
  --border:        oklch(22% 0.055 266 / 0.12);
  --border-hover:  oklch(22% 0.055 266 / 0.32);
  --border-night:  oklch(96% 0.008 85 / 0.14);

  /* Text */
  --text:           oklch(22% 0.055 266);
  --text-secondary: oklch(40% 0.035 266);
  --text-tertiary:  oklch(55% 0.02 266);
  --on-night:       oklch(96% 0.008 85);
  --on-night-2:     oklch(78% 0.025 266);

  /* Accent – brass from the logo */
  --accent:        oklch(74% 0.125 80);
  --accent-hover:  oklch(80% 0.11 85);
  --accent-ink:    oklch(50% 0.10 72);      /* brass text on paper (AA) */

  /* RGB helpers for rgba()/color-mix fallbacks */
  --bg-rgb: 248, 246, 242;
  --night-rgb: 17, 22, 46;
  --accent-rgb: 207, 160, 64;

  /* Semantic */
  --success: oklch(62% 0.14 150);
  --error:   oklch(58% 0.19 27);
  --warning: oklch(78% 0.14 75);
  --focus:   oklch(66% 0.16 245);
  --sheen:   oklch(100% 0 0 / 0.7);
}
```

**Color Rules:**
- Every colour in components is `var(--…)`; zero hex in page CSS/HTML (favicon data-URI is the only exception).
- Brass is for action and sparkle only: CTAs, the sparkle mark, one keyword per hero. Never large brass backgrounds except the CTA band.
- Dark sections are `--night`, never pure black. Text on photos always sits on a night scrim ≥ 55%.

## 3. Typography Rules

```css
@import url('https://fonts.googleapis.com/css2?family=Karantina:wght@400;700&family=Miriam+Libre:wght@400;700&display=swap');
--font-display: "Karantina", "Miriam Libre", sans-serif;
--font-body: "Miriam Libre", "Arial Hebrew", system-ui, sans-serif;
```

| Role | Font | Size | Weight | Line Height | Letter Spacing |
|------|------|------|--------|-------------|----------------|
| Hero H1 | Karantina | clamp(4rem, 11vw, 9.5rem) | 700 | 0.88 | 0 |
| Service H1 | Karantina | clamp(3.25rem, 8vw, 6.5rem) | 700 | 0.9 | 0 |
| Section H2 | Karantina | clamp(2.75rem, 5.5vw, 4.5rem) | 700 | 0.92 | 0 |
| H3 | Karantina | 2rem | 700 | 1 | — |
| Body | Miriam Libre | 1.0625rem | 400 | 1.75 | — |
| Label | Miriam Libre | 0.8125rem | 700 | 1.4 | 0.04em |
| Numbers | Miriam Libre | inherit | 700 | — | tabular-nums, LTR-isolated |

**Typography Rules:**
- Display ≥ 60px on landing hero (Karantina is condensed, so it runs larger than usual).
- Hebrew body line-height ≥ 1.7; no letter-spacing on Hebrew body text.
- Phone numbers always `dir=ltr` isolated.
- **NEVER use**: Heebo, Assistant, Rubik, Open Sans Hebrew (overused), italic Hebrew, all-caps Latin labels.

**Text Decoration (text-decoration-rules.md, Warm Professional column):**
- Hero h1: no gradient; soft shadow only when on photo (`0 2px 18px rgb(var(--night-rgb) / .45)`).
- H2: no gradient, no shadow. One brass keyword `<em>` allowed per H2.
- Body: no decoration.

## 4. Component Stylings

### Buttons
Pressable 3D: solid edge shadow `0 var(--lift) 0 var(--btn-edge)` + soft drop shadow; hover lifts 1px, active sinks by `--lift` and the edge disappears. Gold (night text), light (night text, green WhatsApp glyph), ink (paper text).

```css
.btn{display:inline-flex;align-items:center;gap:.5rem;min-height:48px;padding:0 1.5rem;border-radius:999px;font:700 1.0625rem/1 var(--font-body);border:2px solid transparent;text-decoration:none;cursor:pointer;transition:background-color .18s var(--ease-out),border-color .18s,color .18s,transform .18s}
.btn-gold{background:var(--accent);color:var(--night)}
.btn-gold:hover{background:var(--accent-hover)}
.btn-gold:active{transform:translateY(1px) scale(.98)}
.btn:focus-visible{outline:3px solid var(--focus);outline-offset:3px}
.btn[disabled],.btn[aria-disabled=true]{opacity:.45;cursor:not-allowed;transform:none}
.btn-ghost{border-color:var(--border-night);color:var(--on-night)}
.btn-ghost:hover{border-color:var(--on-night);background:var(--night-2)}
.btn-ink{background:var(--text);color:var(--bg)}
.btn-ink:hover{background:var(--night-3)}
```

### Cards (service cards – SpotlightCard)
```css
.card{position:relative;border-radius:22px;overflow:hidden;background:var(--night);color:var(--on-night);isolation:isolate;transition:transform .45s var(--ease-out)}
.card::after{content:"";position:absolute;inset:0;background:radial-gradient(420px circle at var(--mx,50%) var(--my,50%),rgb(var(--accent-rgb)/.22),transparent 60%);opacity:0;transition:opacity .3s}
.card:hover{transform:translateY(-4px)} .card:hover::after{opacity:1}
.card:hover img{transform:scale(1.04)}
.card:focus-within{outline:3px solid var(--focus);outline-offset:3px}
```

### Navigation
```css
.nav{position:fixed;top:12px;inset-inline:0;z-index:40}
.nav-bar{background:rgb(var(--night-rgb)/.78);backdrop-filter:blur(12px);border:1px solid var(--border-night);border-radius:999px}
.nav.scrolled .nav-bar{background:rgb(var(--night-rgb)/.92);box-shadow:var(--shadow-2)}
/* Services dropdown: <details> on desktop, full sheet on mobile */
```

### Links
```css
.link{color:var(--accent-ink);text-decoration:underline;text-decoration-thickness:1px;text-underline-offset:.25em;transition:text-decoration-color .18s,text-underline-offset .18s}
.link:hover{text-underline-offset:.4em}
```

### Tags / Badges
```css
.tag{display:inline-flex;align-items:center;gap:.4rem;padding:.35rem .8rem;border-radius:999px;font:700 .8125rem/1 var(--font-body);background:var(--surface-alt);color:var(--text-secondary)}
.tag-night{background:var(--night-2);color:var(--on-night-2)}
```

### Before / After slider
```css
.ba{position:relative;aspect-ratio:3/2;border-radius:22px;overflow:hidden;touch-action:pan-y}
.ba-after{clip-path:inset(0 0 0 var(--pos,50%))}
.ba-handle{position:absolute;inset-block:0;inset-inline-start:var(--pos);width:3px;background:var(--accent)}
.ba input[type=range]{position:absolute;inset:0;opacity:0;cursor:ew-resize} /* keyboard + a11y for free */
.ba:focus-within .ba-knob{outline:3px solid var(--focus)}
```

### Form (WhatsApp lead)
Inputs 48px min-height, 12px radius, `--border` → `--border-hover` on hover, focus ring `--focus`, `aria-invalid` turns border `--error`.

## 5. Layout Principles

- Container: `min(1240px, 100% - 2rem)`; text column `min(68ch, 100%)`.
- Section padding: `clamp(4.5rem, 9vw, 7.5rem)` block.
- Component gap: 1rem (cards) / 1.5rem (groups) / 3rem (blocks).
- Card padding: 1.5rem → 2rem desktop.

```css
.bento{display:grid;gap:1rem;grid-template-columns:repeat(6,1fr);grid-auto-rows:minmax(220px,auto)}
.bento .b-xl{grid-column:span 4;grid-row:span 2} .bento .b-l{grid-column:span 2;grid-row:span 2}
.bento .b-m{grid-column:span 2}
@media (max-width:900px){.bento{grid-template-columns:repeat(2,1fr)} .bento>*{grid-column:span 2!important;grid-row:auto!important}}
```

Pages: `/` home + 9 service pages at `/<slug>/index.html` (clean URLs on Vercel and GitHub Pages).

## 6. Depth & Elevation

| Level | Treatment | Use |
|-------|-----------|-----|
| Flat | none | paper sections, text |
| Subtle | `0 1px 2px rgb(var(--night-rgb)/.06), 0 4px 14px rgb(var(--night-rgb)/.06)` (`--shadow-1`) | form, FAQ items |
| Elevated | `0 10px 30px rgb(var(--night-rgb)/.16)` (`--shadow-2`) | scrolled nav, hovered cards |
| Floating | `0 24px 60px rgb(var(--night-rgb)/.28)` (`--shadow-3`) | mobile dock, mega menu |

## 7. Animation & Interaction

**Motion Philosophy**: one gleam, many quiet entrances — only `opacity`, `transform`, `clip-path`, `background-position`.
**Tier**: L2

Signature set (motion-library "Warm Professional" row):
| Category | Effect | Where |
|----------|--------|-------|
| Text – Hero H1 | SplitText (word rise, 70ms stagger) | every page H1 |
| Text – H2 | ScrollFloat (words float up when the H2 enters) | all H2 |
| Text – Body | ScrollReveal (lead paragraphs fade line-by-line) | `.lead` |
| Element | Magnet (CTA pulls toward pointer, rAF) + ClickSpark (logo 4-point sparkles on CTA click) | primary CTAs |
| Component | SpotlightCard bento + Before/After "polish" slider | home services, service pages |
| Background | Grainient (slow drifting radial gradients + SVG grain) | hero |

Landing "爆点" map: (1) hero – word-rise H1 over a real finished-apartment photo with a light sheen sweeping across the floor; (2) first scroll – giant Karantina marquee of services with brass sparkles; (3) list – irregular Bento with spotlight. **巧思**: drag the before/after handle to the end and the floor throws a sparkle burst + "מבריק." tooltip.

```js
// Reveal
const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}}),{rootMargin:'0px 0px -12% 0px'});
document.querySelectorAll('[data-reveal],[data-split],.lead').forEach(el=>io.observe(el));
// Nav state
addEventListener('scroll',()=>nav.classList.toggle('scrolled',scrollY>24),{passive:true});
// Parallax: hero photo translateY(scrollY*.12) via rAF, hover:hover only
```

```css
.w{display:inline-block;transform:translateY(.6em);opacity:0;transition:transform .9s var(--ease-out),opacity .9s var(--ease-out);transition-delay:calc(var(--i)*70ms)}
.in .w{transform:none;opacity:1}
[data-reveal]{opacity:0;transform:translateY(24px);transition:opacity .8s var(--ease-out),transform .8s var(--ease-out)}
[data-reveal].in{opacity:1;transform:none}
```

**Reduced Motion**
```css
@media (prefers-reduced-motion: reduce){
  *,*::before,*::after{animation:none!important;transition:none!important}
  .w,[data-reveal],.lead span{opacity:1!important;transform:none!important}
  .marquee-track{animation:none;flex-wrap:wrap}
}
```
JS checks `matchMedia('(prefers-reduced-motion: reduce)')` and skips Magnet, parallax and sparks.

## 8. Do's and Don'ts

### Do
- Use real-looking job photos (people from behind / hands, Israeli apartments, no readable text).
- Every service page answers: what it includes, how it goes, how long, FAQ, related services, contact.
- Keep phone + WhatsApp one tap away on mobile (dock).
- Write Hebrew in plain dugri voice: "אנחנו", short sentences.
- Unique `<title>`, description, canonical, JSON-LD (Service + FAQPage + BreadcrumbList) per page.

### Don't
- ❌ No invented numbers (years, jobs done, ratings) and no fake testimonials.
- ❌ No eyebrow labels above every heading; no italic headings.
- ❌ No `filter: blur()` on moving elements; backdrop blur ≤ 14px only on nav.
- ❌ No emoji icons; inline SVG only.
- ❌ No solid-colour placeholder blocks instead of images.
- ❌ No scroll-jacking, no pinned sections, no WebGL.
- ❌ No gradient text, no glow on headings.
- ❌ No price promises or city-specific claims the business has not confirmed (copy says "בכל הארץ").
- ❌ No hard-coded colours in components.
- ❌ No long dashes (– —) anywhere in copy; use comma, colon or a full stop. Reads as AI text.
- ❌ No arrow icons in buttons or links; text only. Slider knob uses grip bars, not chevrons.
- ❌ No middle dots (·) as separators in copy.

## 9. Responsive Behavior

| Name | Width | Key Changes |
|------|-------|-------------|
| Desktop | > 1024px | split hero, 6-col bento, mega menu |
| Tablet | 640–1024px | stacked hero, 2-col bento |
| Mobile | < 640px | single column, nav collapses to menu sheet, sticky call/WhatsApp dock, marquee smaller |

**Touch Targets:** minimum 44×44px (buttons 48px).
**Collapsing Strategy:** nav links → "שירותים" sheet; bento → single column; process steps → vertical list; slider stays full width with range input for touch.
No horizontal overflow at 320px (checked with `document.documentElement.scrollWidth`).
