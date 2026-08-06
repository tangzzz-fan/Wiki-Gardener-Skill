# PowerPoint Conversion

Read this file only when converting a `.pptx` presentation.

## Extract and Confirm

1. Run:

   ```bash
   python scripts/extract-pptx.py <input.pptx> <output_dir>
   ```

2. If the import dependency is missing, install it with `pip install python-pptx`, then rerun extraction.
3. Present the extracted slide titles, content summaries, and image counts to the user.
4. Ask the user to confirm the extracted material before designing the HTML deck.

The extraction utility is [../scripts/extract-pptx.py](../scripts/extract-pptx.py).

## Continue Through Shared Phases

After confirmation:

1. Read [visual-discovery.md](visual-discovery.md) and run the same visual comparison used for a new deck.
2. Read [implementation-delivery.md](implementation-delivery.md) and generate the selected style as a fixed-stage HTML presentation.
3. Preserve all source text, extracted images from `assets/`, slide order, and speaker notes. Store speaker notes as HTML comments.
4. Verify converted assets use embeddable data or relative paths so browser rendering, deployment, and PDF export remain intact.

Conversion is complete only when the user-confirmed source material is preserved and the generated deck passes all implementation verification checks.
