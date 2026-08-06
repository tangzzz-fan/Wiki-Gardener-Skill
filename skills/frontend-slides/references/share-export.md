# Share and Export

Read this file only after delivery when the user chooses live deployment, PDF export, or both. If the user declines sharing and export, stop.

## Offer

Ask: "Would you like to share this presentation? I can deploy it to a live URL that works on phones and computers, export it as a PDF, do both, or leave it as HTML."

## Deploy to a Live URL

Deployment uses Vercel and [../scripts/deploy.sh](../scripts/deploy.sh).

1. Check the CLI with `npx vercel --version`. If unavailable, install Node.js first, using `brew install node` on macOS or https://nodejs.org on other systems.
2. Check authentication with `npx vercel whoami`.
3. If unauthenticated, explain that a Vercel account is required:
   - Ask the user to sign up at https://vercel.com/signup with GitHub, Google, or email.
   - Run `vercel login` and follow the browser authorization.
   - Confirm with `vercel whoami`.
   - Wait for user confirmation before deploying.
4. Deploy a folder containing `index.html`, or a single HTML file:

   ```bash
   bash scripts/deploy.sh <path-to-presentation>
   ```

5. Return the live URL, explain that it works on phones, tablets, and computers, and point to https://vercel.com/dashboard for later project removal.

### Deployment Checks

- Local images and videos must travel with the HTML. The script detects normal `src="..."` references, but CSS backgrounds and unusual paths may be missed.
- Prefer deploying the entire presentation folder when it has several assets.
- Verify the deployed URL and every image. If an asset is broken, place the HTML and assets in one folder and deploy that folder.
- Filenames with spaces are encoded as `%20`; if an asset still fails, rename it with hyphens.
- Redeploying the same presentation updates the existing project URL.

## Export to PDF

PDF export uses [../scripts/export-pdf.sh](../scripts/export-pdf.sh). Explain that the PDF is a static snapshot: animations and interactions are replaced by their final visual states.

Run:

```bash
bash scripts/export-pdf.sh <path-to-html> [output.pdf]
```

If no output path is supplied, the PDF is saved beside the HTML. The script opens the deck in a headless browser at 1920×1080, captures each `.slide`, combines the images, and opens the result. It installs Playwright automatically when needed.

### PDF Checks and Recovery

- Warn that the first run may take 30–60 seconds while Playwright downloads Chromium, approximately 150 MB.
- If Chromium installation fails, run `npx playwright install chromium`. If that also fails, report the likely network or firewall issue.
- Ensure slides use `class="slide"` or the exporter will report zero slides.
- Keep local image paths relative. The script serves the HTML's parent directory over HTTP, so relative paths and filenames with spaces work.
- If images are missing, verify the files exist and the HTML uses relative paths rather than absolute filesystem paths.
- Report the PDF path, size, and static-animation limitation.

An 18-slide deck may produce a PDF around 20 MB because each slide is captured at 1920×1080. If the output exceeds 10 MB, offer compression. On approval, run:

```bash
bash scripts/export-pdf.sh <path-to-html> [output.pdf] --compact
```

Compact mode renders at 1280×720 and typically reduces size by 50–70 percent with a modest sharpness tradeoff.
