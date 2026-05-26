# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Static single-page portfolio site for AKM Fazlay Rabby (RABBYZ). No build system, no dependencies, no bundler — pure HTML/CSS/JS in one file.

Both `index.html` (root) and `web/index.html` are identical copies. The canonical source is `web/index.html`; after editing, sync to root before every commit:

```bash
cp web/index.html index.html
```

GitHub Pages serves from root — if root is stale, the live site won't update.

## Running Locally

Open `index.html` directly in a browser, or serve with any static file server:

```bash
python -m http.server 8001
```

## Architecture

Everything lives in `index.html`:

- **CSS custom properties** at `:root` — all colours (`--bg-*`, `--ink-*`, `--accent`), fonts, spacing (`--section-y: 9rem`, `--r: 18px`)
- **Fonts** via Google Fonts: Syne (display/body), JetBrains Mono, Instrument Serif
- **Sections** in order: hero → marquee → about → career → projects → now → contact → footer
- **JS** (inline, ~50 lines): kinetic wordmark hover, cursor-tracked blob, IntersectionObserver scroll reveals, smooth scroll

## Key Design Constraints

- Accent colour is `#00ff88` — all hover states, glows, and gradients derive from `--accent` / `--accent-glow` / `--accent-soft`
- `.reveal` class elements start hidden (`opacity:0; transform:translateY(20px)`) and animate in via IntersectionObserver adding `.in`
- `.fadeup` is hero-only entry animation (CSS, no JS)
- Marquee seamless loop requires the track items to be duplicated exactly — first and second halves must match
- `.project-card.nextor` has a distinct green-tinted background for the NexTor project cards
- Grid layouts (`.about-grid`, `.project-grid`, `.focus-grid`, `.contact-grid`) collapse to single-column at `max-width: 800px`
- Nav links (About/Work/Now) hide at `max-width: 667px` — only brand + CTA remain
- Mobile overrides at `max-width: 430px` — targets iPhone 16 Pro/Pro Max; blob hidden, `100svh` hero, tighter spacing
- Footer has hits.sh visitor badge: `hits.sh/rabbyz.com.svg` with `color=00ff88`
