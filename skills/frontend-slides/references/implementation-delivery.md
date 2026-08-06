# Implementation and Delivery

Read this file after visual discovery or when enhancing an existing HTML presentation.

## Enhancement Rules

Before changing an existing deck, inspect its structure, count current elements, and compare each slide with the selected density limits.

- Fit added images inside the 1920×1080 stage. If a slide is already full, reduce other content or move the image to a new slide.
- Keep text to roughly 4–6 bullets per slide unless a verified high-density layout supports more. Split excess into continuation slides.
- Preserve the deck's existing intent while enforcing the fixed-stage invariants.
- After every substantive change, verify the stage remains 16:9, text stays inside its containers, panels do not overlap, and screenshots are correct at 1280×720 and one phone viewport.
- Reorganize content before overflow occurs and tell the user when slides were split.

## Generate the Full Deck

Generate from the confirmed content, curated images, density, and selected visual direction. If no images were provided, use CSS-generated gradients, shapes, patterns, and contextual graphics as a first-class visual path.

Apply density consistently:

- **Low density / speaker-led:** More slides, fewer ideas per slide, large headings, short phrases, visual metaphors, section beats, statements, and presenter-friendly pacing.
- **High density / reading-first:** Self-contained slides, structured grids, comparison tables, annotated diagrams, captions, and concise explanatory copy.

If a high-density slide becomes cluttered, split or redesign it. Do not shrink it into illegibility.

## Apply the Selected Design

For a selected bold template, read only that template's `design.md` and treat it as the design recipe:

- Preserve fonts, palette, decorative vocabulary, spacing rhythm, and component grammar.
- Translate any viewport-fluid values into fixed 1920×1080 coordinates. Do not retain viewport reflow in the final deck.
- Keep the final output a single self-contained HTML file.
- Do not copy demonstration content or mimic the source template literally.
- Read `template.html` only as a last-resort implementation reference.

For a selected custom wildcard, use the preview's CSS and layout as the recipe:

- Preserve its typography, palette, decorative vocabulary, spacing rhythm, grid logic, and component grammar.
- Expand that system across the full deck instead of switching to a preset or template.
- Design missing slide layouts from the same system.

## Required Supporting Files

Before generating, read:

- [../html-template.md](../html-template.md) for HTML architecture, JavaScript features, inline editing, and code-quality rules.
- [../viewport-base.css](../viewport-base.css) and include its full contents in the final `<style>` block.
- [../animation-patterns.md](../animation-patterns.md) for motion patterns suited to the selected feeling.

The final deck must:

- Contain all CSS and JavaScript inline.
- Use Fontshare or Google Fonts rather than system fonts.
- Use detailed `/* === SECTION NAME === */` comment blocks.
- Use `.slide` elements so PDF export can discover every slide.
- Keep local media paths relative when assets cannot be embedded.

## Visual Verification

Render and inspect screenshots rather than relying only on DOM metrics:

1. Check every slide for content overflow.
2. Check grid and positioned panels for visual overlap; `scrollHeight` alone cannot detect panels covering each other.
3. Check desktop rendering at 1280×720.
4. Check one phone viewport and confirm the fixed 16:9 stage scales without reflow.
5. Test keyboard navigation, any swipe or tap navigation, animations, reduced-motion behavior, and inline editing.

Implementation is complete only when every slide passes these checks.

## Delivery

1. Delete `.frontend-slides/slide-previews/` if it exists.
2. Open the final HTML in a browser.
3. Tell the user the file location, style name, and slide count.
4. Explain navigation: arrow keys, Space, and swipe or tap when implemented.
5. Explain customization through `:root` color variables, the font link, and `.reveal` animation classes.
6. Explain inline editing: hover near the top-left or press E, click text to edit, and press Ctrl+S to save.
7. Offer revisions, direct browser editing, and the optional share/export branch.
