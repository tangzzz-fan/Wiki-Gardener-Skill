# Content and Visual Discovery

Read this file for new presentations and after a PowerPoint extraction has been confirmed. Complete content discovery before style discovery.

## Content Discovery

Ask all questions together. Use a native structured-question UI when available; otherwise use one concise numbered message:

1. **Purpose:** Pitch deck / Teaching or tutorial / Conference talk / Internal presentation
2. **Length:** Short 5–10 / Medium 10–20 / Long 20+
3. **Content:** All content ready / Rough notes / Topic only
4. **Density:** Low density / speaker-led, or High density / reading-first

If the user has content, ask them to share it. Remember the density choice because it determines slide count, typography scale, text volume, layout density, and pacing.

Do not ask about inline editing before the draft. Include inline editing by default unless the user explicitly requests a locked or export-only file.

### Image Evaluation

If the user provides an image folder:

1. List image files such as PNG, JPG, SVG, and WebP.
2. Inspect each image using available image understanding. If unavailable, use filenames and metadata, asking for clarification only when necessary.
3. Record what each image shows, whether it is usable and why, the represented concept, and dominant colors.
4. Co-design the outline from text and curated images together. Do not plan the full deck first and append images afterward.
5. Confirm the outline and selection: Looks good / Adjust images / Adjust outline.

If a usable logo exists, embed it as base64 in each style preview so every option demonstrates the user's brand.

## Style Discovery

Generate three distinct, single-slide HTML previews directly. Each must show typography, colors, motion, and the overall visual system through a real title slide.

Do not ask whether the user wants options or a preset picker. If the user supplied a vibe, follow it; otherwise infer mood from occasion, audience, content, and stakes. If the user names a preset or bold template, include it as one option and make the other options meaningfully different.

### Progressive Template Loading

1. Read [../STYLE_PRESETS.md](../STYLE_PRESETS.md) for safe candidates.
2. If present, read [../bold-template-pack/selection-index.json](../bold-template-pack/selection-index.json).
3. Match candidates using `mood`, `tone`, `best_for`, `avoid_for`, `formality`, `density`, and `scheme`. Treat `best_for` examples as soft signals rather than industry filters.
4. Read only shortlisted `preview.md` files from the index.
5. Use `preview.md` only to create title-slide previews. Do not read any full `design.md` yet.
6. After the user selects a bold template, the implementation branch may read only that template's `design.md`.
7. Read `template.html` only if the selected `design.md` lacks a critical implementation detail.

### Preview Mix

Generate by default:

- One safe preset from `STYLE_PRESETS.md`.
- At least one bold template from the selection index.
- One wildcard: either a second bold template or a self-generated custom design, whichever creates the strongest useful contrast.

For conservative or high-stakes decks, keep all options authoritative and make the safe option especially restrained. For expressive decks, retain a readable safe fallback and make the wildcard adventurous and specific. If bold-template matches are weak, use a custom wildcard or another safe preset instead of forcing a template.

### Custom Wildcard

A custom direction must:

- Match the occasion, audience, mood, and density.
- Use distinctive typography rather than Arial, Inter, Roboto, system fonts, or repeatedly defaulting to Space Grotesk.
- Commit to a palette and avoid clichéd purple gradients on white.
- Establish a recognizable layout system and one strong atmospheric or graphic device.
- Extend plausibly to section, content, quote, comparison, and closing slides.
- Follow the fixed 1920×1080 stage and all authenticity checks.
- Avoid rendering process labels such as "custom", "wildcard", or "AI-generated".

### Preview Authenticity

Every preview must look like the user's real opening slide, not a diagnostic card:

- Keep internal workflow text off the slide, including `preview`, `generated from`, `preview.md`, `template`, `preset`, `style option`, option letters, filenames, paths, and source labels.
- Keep template and slug names in the user-facing message, never on the slide.
- Do not render requirement notes such as "safe option", "bold option", or audience metadata unless the user explicitly wants that phrase in the deck.
- Use only genuine deck chrome: deck title, section title, date, author, company, page number, or a phrase from the source content.
- Inspect visible text and remove internal metadata before opening the previews.

Save self-contained previews to `.frontend-slides/slide-previews/style-a.html`, `style-b.html`, and `style-c.html`, then open all three.

Ask which style the user prefers: Style A / Style B / Style C / Mix elements. If they choose a mix, ask which elements to combine. Style discovery is complete only after the user selects or specifies a direction.
