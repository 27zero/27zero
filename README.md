# 27zero.agency — Static Site Source

This is the source for the rebuilt site, starting with the EdTech Marketing
section. It's a small Python build script over Jinja2 templates — the
*output* is 100% plain static HTML with no framework, no server, and no
runtime dependency. The build step exists only so the nav, footer, and
repeated page patterns live in one place instead of being copy-pasted into
every file.

## Folder structure

```
27zero-site/
├── build.py                  ← run this to generate the site
├── templates/
│   ├── base.html              ← shared <head>, nav, footer — every page extends this
│   └── macros.html            ← reusable blocks: hero, CTA footer, deliverable cards, etc.
├── pages/
│   └── edtech-marketing/      ← one folder per section; 13 page templates live here
├── assets/
│   └── css/style.css          ← the one stylesheet every page links to
└── dist/                      ← generated output — this is what you publish
```

## Requirements

- Python 3
- Jinja2 (`pip install jinja2`)

## Running this on your laptop

You need Python (free, and likely already on your Mac — Windows usually
needs a quick install). Everything below is a one-time setup, then two
commands you'll reuse going forward.

### 1. Check if you have Python

Open Terminal (Mac) or Command Prompt / PowerShell (Windows) and run:

```
python3 --version
```

If you see a version number (3.8 or higher), you're set — skip to step 2.
If you get an error:

- **Mac**: install from [python.org/downloads](https://www.python.org/downloads/),
  or run `brew install python3` if you have Homebrew.
- **Windows**: install from [python.org/downloads](https://www.python.org/downloads/).
  During setup, check the box that says **"Add Python to PATH"** — easy to
  miss, but it's what makes the `python3` command work afterward. (On
  Windows the command is sometimes `python` instead of `python3` — try
  whichever responds to `--version`.)

### 2. Install Jinja2 (one time only)

```
pip3 install jinja2
```

(Windows: `pip install jinja2` if `pip3` isn't recognized.)

### 3. Unzip the project and build the site

Unzip `27zero-site.zip` anywhere on your laptop, then in Terminal/Command
Prompt, move into that folder and build:

```
cd path/to/27zero-site
python3 build.py
```

You'll see a line printed for each of the 13 pages, then `Done`. This
regenerates `dist/` — the actual publishable site — from the templates.

### 4. Preview it in your browser

```
python3 build.py serve
```

This builds the site and opens it at `http://localhost:8000` in your
default browser automatically. Click around — the nav, all 13 pages, and
the styling should look exactly like what you reviewed in the chat.
Leave the Terminal window open while previewing; press `Ctrl+C` in it to
stop the server when you're done.

If port 8000 is already busy on your machine, use a different one:

```
python3 build.py serve 8080
```

### Why you can't just double-click an HTML file

Every internal link and the stylesheet reference start with `/` (like
`/assets/css/style.css`) so they resolve correctly once this is deployed
to a real domain. Opening a file directly from your hard drive
(`file:///Users/you/27zero-site/dist/...`) makes the browser treat that
leading `/` as your hard drive's root instead of the site's root, so the
styling won't load. This is true of every static site tool (Hugo, Jekyll,
Next.js, etc.), not specific to this setup — the local server in step 4 is
the standard fix, and it's exactly how the real host will serve it later.

---

## Adding or rebuilding a section

This is the "integrate changes progressively" part. To bring a new section
(Work, About, Resources, an EdTech Mentor interview, etc.) into this same
system:

1. Make a folder under `pages/` for the section if one doesn't exist yet
   (e.g. `pages/work/`).
2. Write each page as a template that extends the shared layout:

   ```jinja
   {% extends "base.html" %}
   {% from "macros.html" import hero, cta_footer %}
   {% block title %}Page Title — 27zero{% endblock %}
   {% block content %}
   {{ hero("Eyebrow text", "/parent-link", "Headline", "Subhead text") }}
   ... rest of the page ...
   {{ cta_footer("Closing line") }}
   {% endblock %}
   ```

3. Add one line to the `PAGES` list at the top of `build.py`:
   `("work/overview.html", "work")`
4. Run `python3 build.py` again.

Everything else — nav, footer, fonts, the CSS file, the button and card
styles — is already shared, so a new section automatically looks and
behaves like the rest of the site.

## Changing something site-wide

- **Nav links, footer text, fonts**: edit `templates/base.html`.
- **Colors, spacing, component styles**: edit `assets/css/style.css`
  (everything is driven off the `:root` custom properties at the top —
  change `--violet` once, every button/link/accent updates).
- **Repeated structural pieces** (hero sections, the CTA block, the
  deliverable-card grid, the "belongs to" link): edit `templates/macros.html`.

Rebuild after any of the above with `python3 build.py`.

## Publishing

`dist/` is the entire publishable site. Upload its contents to:

- **Netlify / Vercel / Cloudflare Pages** — connect the repo and point the
  build command at `python3 build.py`, publish directory `dist`. Or just
  drag-and-drop the `dist/` folder for a manual deploy.
- **GitHub Pages** — push `dist/` to the `gh-pages` branch (or configure
  Pages to serve from a `/dist` folder).
- **Any traditional web host** — upload the contents of `dist/` to the
  document root via FTP/SFTP.

None of these require Python or Jinja2 on the server — those are only
needed locally (or in CI) to *generate* `dist/`. The published site is
just files.

## What's built so far

- `/` — Home
- `/work/` — portfolio index (13 case studies) + all 13 individual case study pages, each with real Brief/Challenge/Solution/Impact content. 3 of the 13 (Anthology Marketing Programs, Busuu, Universidad de los Andes) have real working YouTube/Vimeo video embeds — these platforms support cross-site embedding, unlike Webflow's own CDN (see note below).
- `/about/` — mission, differentiators, the 10-person team, and a bridge into EdTech Marketing. Rewritten rather than literally cloned: the original About page had a real bug (the same placeholder paragraph duplicated across 7 different "capability" categories) and referenced the old 4-category service structure this project already replaced — neither was worth reproducing.
- `/lets-talk/` — contact page with both offices and both CTAs (strategy session booking + EdTech Mentor LinkedIn newsletter)
- `/edtech-marketing-agency/` — section overview + 3 practice pages + 9 service pages
- `/resources/` — index + 16 articles (1 pillar guide built in full long-form depth; the other 15 built from substantial real excerpt content gathered from the live index page rather than each individual page — see note below). The original site's broken `[LINK: ...]` placeholder text is fixed into real working hyperlinks throughout.
- `/edtech-mentor-interviews/` — hub page with a real, accurate 24-person roster, and 1 fully published interview (Frederico Bello) built from the complete original Q&A — see note below for the other ~65.

## A note on Resources' depth

The live site's Resources index page happened to include full teaser excerpts for all 16 articles directly in its markup. The pillar article ("EdTech Marketing Agency") was fetched and rebuilt in full — it's a genuine 2,500+ word piece with all 9 original sections intact. The other 15 are built from their real, substantial excerpt paragraphs (each 80–200 words of genuine, specific, on-topic content — not filler) rather than each one's full ~2,000-word body, since Resources is secondary SEO content rather than flagship work. If you want any of these expanded to full depth, point me at which ones and I'll fetch and rebuild them properly.

## Preview server now supports video

`python3 build.py serve` uses a custom request handler (`RangeHTTPRequestHandler`) that properly supports HTTP Range requests — required for `<video>`/`<audio>` elements to load and play correctly. Plain Python `http.server` ignores Range headers entirely and always returns the full file, which leaves video elements stuck never loading metadata. This was a real bug, found and fixed while adding the home page's hero video — not just a cosmetic change.

The home page hero now has the real background video (`assets/videos/27zero-hero-loop.mp4`, self-hosted — no Webflow CDN dependency) with a poster frame (`assets/images/hero-poster.jpg`) shown before playback starts and for users with `prefers-reduced-motion` set, in which case the video doesn't autoplay at all and the poster is the final state. This is scoped entirely to the home page (`.hero-home-video` modifier class) — the other 48 pages are unaffected.

One caveat worth knowing: I cannot visually confirm smooth video *motion* from this environment — my testing browser (Playwright's bundled Chromium) lacks H.264 decoding support, a known limitation of open-source Chromium builds (real Chrome, Safari, Firefox, Edge all support H.264 natively, so this isn't a concern for actual visitors). I verified the underlying pipeline is correct using a differently-encoded test clip the testing browser *could* decode — confirmed full playback (`readyState: 4`, actively playing, correct duration) — so the only unverified piece from my end is literally just "does the motion look smooth," which is worth a quick check in your own browser.

The live hub lists roughly 80 unique interviewees. Each individual interview is a full, real Q&A — Frederico Bello's alone (the one built here in full) runs to about 4,000 words, with pull-quote callouts throughout, similar in scope to a long magazine profile. Building all ~80 at this fidelity is a real multi-session undertaking, not something to compress without losing what makes the series valuable in the first place.

What's here now: a hub page with an accurate 24-person roster (real names, real titles, real companies — not a placeholder list), and one complete interview built end-to-end as the proven template. Adding more is mechanical from here: fetch the interview, drop it into `pages/edtech-mentor/[slug].html` following the Frederico Bello template, add one line to `build.py`. Worth deciding which voices matter most to have live first — the ones tied to existing case study clients (David Meek/Student First, Wesley Matthews/Doctums, Jonathan Fry/Scholarship Magic) are a natural starting point since they reinforce the Work section.

## Important: the live site's CDN blocks external embedding

Every asset on `cdn.prod.website-files.com` — images, team photos, the homepage video — returns `403 Forbidden` when requested from any origin other than the live Webflow site itself. This was confirmed directly (not assumed) using a headless browser to inspect actual network responses. It affects the **entire domain**, not just one folder.

Practical effect: nothing from that CDN can be hotlinked into this project, full stop. Every page in this project is built without it — real content and copy throughout, but illustrations/graphics are done as self-contained inline SVG (see the Venn diagram on the EdTech Marketing overview, the circle motif on the EdTech Mentor and team cards) rather than referencing the original images. The one exception is the 3 case studies with real YouTube/Vimeo embeds, since those platforms are built for cross-site embedding.

If you want real photos (team headshots, mentor headshots, case study imagery) anywhere in this project, they need to be downloaded from the live site or Webflow's Asset Manager and added to this project's own `/assets/` folder — at which point they'll work anywhere, including production.

## Known gaps on the home page (flagged, not silently faked)

- **Newsletter form** posts to `#` — needs your real HubSpot form/portal ID
  wired in before launch (see the `TODO` comment in
  `pages/home/index.html`).
- **Work and EdTech Mentor links** on the home page point to `/work/...` (now built) and
  `/edtech-mentor-interviews/...` (not yet built) paths.

## What's not migrated yet

**Careers** and the legal pages (Privacy, Security Policy) — small, not yet started. **The EdTech Mentor's remaining ~65 interviews** — intentionally deferred per the note above, with a clear path to add them incrementally. Every other section of the live site (Home, Work, EdTech Marketing, About, Let's Talk, Resources) is now fully represented in this project.
