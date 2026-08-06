---
name: frontend-slides
description: Create animation-rich HTML presentations from scratch or by converting PowerPoint files. Use for presentation, slides, HTML 演示, PPT 转换, PDF 导出, live sharing, or improving an existing web deck. Helps users discover an aesthetic through visual previews.
---

# Frontend Slides

Create zero-dependency, animation-rich HTML presentations that run entirely in the browser.

## Core Constraints

1. **Zero dependencies:** Deliver a single HTML file with inline CSS and JavaScript. No npm or build step.
2. **Visual discovery:** Show concrete previews instead of asking users to describe aesthetics abstractly.
3. **Distinctive design:** Build a context-specific visual system; avoid generic typography, palettes, layouts, and dashboard-like card grids.
4. **Progressive disclosure:** Read lightweight indexes and shortlisted preview cards first. Load a full template `design.md` only after the user selects that template.
5. **Fixed 16:9 stage:** Author every slide at 1920×1080 and scale the stage uniformly to the viewport. Letterboxing is allowed; reflowing slide content is not.

## Fixed Stage Invariants

These rules apply to every new, converted, or enhanced deck:

- Use a viewport wrapper that fills the browser window and a fixed 1920×1080 internal stage.
- Keep slide measurements fixed. Do not use responsive breakpoints to rearrange slide content on phones.
- Include the full contents of [viewport-base.css](viewport-base.css) in the presentation.
- Control slide visibility with `.active` / `.visible` plus `visibility`, `opacity`, and `pointer-events`; do not switch slides with `display: none` / `display: block`.
- Use `clamp()` only outside the stage or in small fallback previews.
- Include `prefers-reduced-motion` support.
- Negate CSS functions with `calc(-1 * clamp(...))`, never `-clamp()`, `-min()`, or `-max()`.
- Keep every slide free of scrolling, overflow, overlapping panels, and uncomfortably small text. Split crowded content into more slides.
- Verify screenshots at 1280×720 and at one phone viewport while preserving the 16:9 stage.

## Phase Router

Detect the mode, then load only the branch needed:

- **Mode A — New presentation:** Gather purpose, length, source-content readiness, and density in one round. Then read `references/visual-discovery.md`, followed by `references/implementation-delivery.md`.
- **Mode B — PPT conversion:** Read `references/ppt-conversion.md`. After extraction and user confirmation, continue through visual discovery and implementation.
- **Mode C — Existing HTML enhancement:** Read `references/implementation-delivery.md`. Preserve the deck's intent, enforce the fixed-stage invariants, and split slides before added content causes crowding.
- **Optional sharing or export:** After delivery, offer live deployment, PDF export, both, or neither. Read `references/share-export.md` only if the user chooses an export branch.

## Density Decision

Ask whether the deck is primarily:

- **Low density / speaker-led:** One idea per slide, large type, generous negative space, and usually 1–3 bullets.
- **High density / reading-first:** Self-contained slides with structured grids, tables, annotations, and usually 4–8 bullets or 4–6 cards when readable.

When needs are mixed, live persuasion defaults to low density; asynchronous circulation or detailed review defaults to high density. Never solve density by shrinking content until it is cramped.

## Required Completion Checks

Before delivery, verify:

1. The output is a self-contained HTML file using the complete fixed-stage CSS.
2. All slides remain 16:9 at desktop and phone viewport sizes.
3. No text overflows its container and no panels overlap.
4. Navigation, animations, reduced-motion behavior, and inline editing work.
5. Preview artifacts are removed and the final deck opens successfully.

## Resource Routes

- Visual discovery uses [STYLE_PRESETS.md](STYLE_PRESETS.md), [bold-template-pack/selection-index.json](bold-template-pack/selection-index.json), and only shortlisted template preview files.
- Implementation uses [html-template.md](html-template.md), [viewport-base.css](viewport-base.css), and [animation-patterns.md](animation-patterns.md).
- PPT conversion uses `scripts/extract-pptx.py`.
- Live deployment uses `scripts/deploy.sh`.
- PDF export uses `scripts/export-pdf.sh`.

## Vault Contract

1. Write decks to vault or workspace `90_export/` by default, unless the user names another path.
2. Never write HTML decks into `20_领域/`.
3. Source material may come from notes or `10_inbox/`; this skill presents it but does not decide knowledge absorption or factual correctness.
4. Keep agent-facing output free of emoji; use text labels such as `[警告]`.

