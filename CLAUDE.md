# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

The public site **rabbyz.com** for AKM Fazlay Rabby (RABBYZ): static HTML/CSS/JS with no build
step, no dependencies and no bundler, served by GitHub Pages from `main`. The repo has two
writers: people edit the pages, and the Morning_News publisher (node `mac` on homeservermac,
its own clone `/home/briefs/rabby_profile`) commits machine output into it twice every
trading day.

| Path | What | Written by |
|---|---|---|
| `web/index.html` | the portfolio page, **canonical source** | hand |
| `index.html` | byte-identical copy of `web/index.html`; this is what Pages serves | `cp` (see below) |
| `brief/index.html` | Market Brief viewer: date picker + morning/evening toggle, loads a brief into an iframe; deep link `?date=YYYY-MM-DD&edition=morning\|evening` | hand |
| `calc/index.html` | Portfolio Avg Calculator (Tailwind from CDN) | hand |
| `briefs/` | `brief_<date>_<edition>.html` + `manifest.json` (`updated`, `briefs[]` sorted ascending) | Morning_News `publish_briefs.py` only |
| `ticker/latest.json` | DSE close ticker data | Morning_News `news/ticker.py` only |
| `tools/refresh_gsec_snapshot.py` | refreshes the GSEC panel's embedded data | hand-run |

Never hand-edit `briefs/` or `ticker/`: the publisher owns them, and its commits (author
`Rabby`, message `briefs: publish market briefs (...)`) are most of the history. It publishes
Sun–Thu about 06:45–09:45 and 16:00–18:00 Dhaka, and on a rejected push it runs
`pull --rebase` once. Edits to the hand-written pages don't conflict with it, but always
`git pull --ff-only` before committing here.

## Commands

```bash
cp web/index.html index.html                 # after every edit to the page, before committing
python -m http.server 8001                   # local preview at http://localhost:8001 (fetches need a server, not file://)
python tools/refresh_gsec_snapshot.py        # pull gsec.rabbyz.com's public API into the GSEC panel (both copies)
python tools/refresh_gsec_snapshot.py --dry-run
```

There are no tests or linters. Check changes in a browser at desktop width and at 393px
(iPhone) for JS errors and horizontal overflow.

**Deploy = push to `main`.** Pages rebuilds in about a minute, but rabbyz.com sits behind
Cloudflare, which can keep serving the old page for several minutes (`CF-Cache-Status: HIT`).
To tell a slow cache from a failed deploy, compare with the origin
`https://rocksonju.github.io/rabby_profile/` and `gh api repos/rocksonju/rabby_profile/pages/builds/latest`.

Files are LF in git; this PC has `core.autocrlf=true`, so keep scripted edits LF.

## Architecture of the portfolio page

Everything is in `web/index.html`: one `<style>`, the markup, one inline `<script>` at the end.

- **CSS custom properties** at `:root`: colours (`--bg-*`, `--ink-*`, `--accent`), fonts, spacing (`--section-y: 9rem`, `--r: 18px`)
- **Fonts** via Google Fonts: Syne (display/body), JetBrains Mono, Instrument Serif
- **Sections** in order: hero → marquee → about → career → projects → live (GSEC Analyzer hero `#gsec`, Market Brief hero `#brief`, then two tool cards) → now → contact → footer, plus the fixed DSE ticker bar after `</main>`
- **Script**, one IIFE per feature: kinetic wordmark, cursor-tracked blob, the GSEC panel, the DSE ticker, the Market Brief panel, IntersectionObserver reveals, smooth scroll. Dynamic content is built with `createElement` / `textContent` (an editor hook here rejects `innerHTML`)

The three live features get their data three different ways:

- **GSEC Analyzer panel** (`#gsec`, orange `--gs` palette): an animated mock of the gsec.rabbyz.com terminal built from an embedded GSOM snapshot, the `const GS_META / GS_YAS / GS_BONDS / GS_CURVE / GS_PREV` lines in the script. Labels and dates follow `GS_META`; the ticks are simulated around the snapshot. gsec.rabbyz.com sends no CORS headers, so the page cannot read it live: refresh with `tools/refresh_gsec_snapshot.py`, which rewrites those lines by regex (keep each one on a single line)
- **Market Brief panel** (`#brief`): fetches `/briefs/manifest.json`, loads the newest edition and the newest of the other edition into `sandbox="allow-same-origin"` iframes, and scrolls them in turn. Counts and the publish stamp come from the manifest; nothing to refresh by hand. The briefs are 640px email-style HTML (inline styles, no classes or scripts), so don't parse them
- **DSE close ticker** (`#dseTk`): fetches `/ticker/latest.json` (indices, breadth, turnover, top 60 by turnover). No file → the bar stays hidden and `body.has-ticker` is not set

All three pause when off-screen or hovered and respect `prefers-reduced-motion`.

## Key Design Constraints

- Accent colour is `#00ff88`: hover states, glows and gradients derive from `--accent` / `--accent-glow` / `--accent-soft`. The GSEC panel's orange is scoped to `.gsec-hero`
- `.reveal` elements start hidden (`opacity:0; transform:translateY(20px)`) and animate in when the IntersectionObserver adds `.in`
- `.fadeup` is the hero-only entry animation (CSS, no JS)
- The marquee's seamless loop needs its track items duplicated exactly: the first and second halves must match. The GSEC board, the GSEC tape and the ticker loop the same way (content appended twice, animated to `-50%`)
- `.project-card.nextor` has a distinct green-tinted background for the NexTor project cards
- Grid layouts (`.about-grid`, `.project-grid`, `.focus-grid`, `.contact-grid`) collapse to one column at `max-width: 800px`; `.live-grid` is two columns, one at 640px; the GSEC and Brief panels stack at 980px
- At `max-width: 667px` every nav link except the "Say hi" CTA hides (`.nav-links li:not(:last-child)`)
- Mobile overrides at `max-width: 430px` target iPhone 16 Pro/Pro Max: blob hidden, `100svh` hero, tighter spacing
- Footer has the hits.sh visitor badge: `hits.sh/rabbyz.com.svg` with `color=00ff88`
