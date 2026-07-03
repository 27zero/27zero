# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Static site generator for 27zero.agency. A Python build script renders Jinja2 templates (some fed by static content, some fed by a Sanity CMS) into plain static HTML in `dist/`. There is no client-side framework, no server, no runtime dependency — the published site is just files. JavaScript exists only for presentation behavior (nav, mobile menu, scroll-reveal, slider drag/arrows, category filtering) and never fetches data or renders markup at runtime.

`ARCHITECTURE.md` is the authoritative deep-dive (module responsibilities, data flow, full "how to add a CMS section" walkthrough). Read it before making structural changes — this file is a shorter operational summary.

## Working rules (mandatory)

These rules govern every change made to this repo, regardless of how small the fix looks.

1. Never replace an existing template wholesale unless the user explicitly asks for that. Prefer a targeted change scoped to the affected module/page.
2. Never change the project's architecture to solve a small problem. Always prefer the minimal fix.
3. Never modify `build.py`, anything under `builders/`, `helpers/`, or the global templates (`templates/base.html`, `templates/macros.html`) if the problem can be resolved inside the specific module or page it's actually in.
4. Never remove existing functionality without explicit approval.
5. Never invent sample data or placeholders when the real data already exists in Sanity — wire it through the normal `helpers/sanity.py` → builder → template path instead (see the JavaScript policy below and Architecture's Sanity note).
6. Never change the site's visual structure without explicit authorization.
7. Don't move files between folders unless strictly necessary for the fix.
8. `build.py` and `builders/base.py` require explicit authorization before *any* modification, however small — they affect the whole build pipeline / every CMS section respectively.

**Before writing any code**, present: root cause, affected files, expected diff, risks, and a rollback plan. If more than one valid solution exists, present them ordered from lowest to highest impact and recommend one. Then wait for explicit approval before editing.

After an approved change, suggest a short Conventional Commits message, e.g. `fix(work): preserve Jinja rendered content`.

## Commands

```bash
python build.py            # build the site into dist/
python build.py serve      # build, then serve dist/ at http://localhost:8000
python build.py serve 3000 # same, on a custom port

pip install -r requirements.txt   # jinja2, requests (only deps)
```

There is no lint/test/typecheck command configured for the Python side — there are no test files in this repo. Verify changes by running a build and checking the generated `dist/` output (or `python build.py serve` and clicking through in a browser).

Sanity Studio (schema editing only, lives in `studio/`, separate Node project):
```bash
cd studio
npm run dev      # local Studio UI
npm run deploy   # deploy Studio
```

## Environment variables

Set in Vercel for production; all have local fallbacks in `config.py` so no `.env` is required to build locally.

| Variable | Purpose | Default |
|----------|---------|---------|
| `SITE_URL` | Canonical base URL | `https://www.27zero.agency` |
| `SANITY_PROJECT_ID` | Sanity project ID | `qjn4zzjc` |
| `SANITY_DATASET` | Sanity dataset | `production` |
| `SANITY_TOKEN` | API token for drafts/private data | `""` |
| `DRAFT_MODE` | Include draft documents | `false` |
| `VERBOSE` | Debug-level build logging | `false` |

## Architecture

**Build pipeline** (`build.py`, orchestrator only — no content logic lives here):
1. Fetch all content from Sanity (`helpers/sanity.py`) — *before* anything touches `dist/`. If any fetch fails, the build aborts and the last successful `dist/` stays live (safety contract: `dist/` is only cleared after every fetch succeeds).
2. Clear and recreate `dist/`.
3. Configure one Jinja2 `Environment` (`FileSystemLoader([pages/, templates/])`, `autoescape=False` — content is escaped manually, templates use `|safe`).
4. `builders/pages.py` renders the static `PAGES` manifest (template path → URL path tuples).
5. `builders/posts.py` (legacy, pre-dates the section-builder abstraction) renders posts, resources, interviews.
6. CMS sections built via `SectionBuilder` subclasses (currently only `WorkBuilder`).
7. `builders/sitemap.py` generates `dist/sitemap.xml` from a builder registry + legacy entries.
8. `builders/rss.py` generates `dist/rss.xml` (posts + resources).
9. `assets/` copied verbatim into `dist/assets/`.

**`builders/base.py` — `SectionBuilder`** is the core abstraction and the most important file to understand before touching CMS-driven sections. It owns everything invariant across sections (build loop, image URL resolution, related-item scoring, category grouping, SEO context, sitemap entries, file writes) so a new CMS section requires only ~60 lines of section-specific code. Subclasses override up to five hooks: `enrich_item`, `body_html`, `index_context`, `detail_context`, `detail_seo`. `builders/work.py` (`WorkBuilder`) is the reference implementation — copy its pattern for any new section rather than starting from scratch. The full "how to add a CMS section" recipe (schema → GROQ query → builder → templates → wire into `build.py`) is in `ARCHITECTURE.md`.

Note: `builders/posts.py` predates `SectionBuilder` and intentionally still uses the older pattern (posts/resources/interviews). It migrates to `SectionBuilder` when its templates get redesigned — don't refactor it opportunistically.

**Config** (`config.py`) is the single source of truth for paths, site identity, and Sanity settings — every module imports constants from here rather than reading `os.environ` or building paths itself.

**Helpers are pure, side-effect-free, no file I/O:**
- `helpers/sanity.py` — all Sanity API access; one GROQ projection + one `get_*()` function per document type. Adding a content type means adding a projection + function here, nothing else.
- `helpers/portable_text.py` — Sanity Portable Text blocks → HTML strings.
- `helpers/seo.py` — builds the `seo` context dict every template consumes (`seo.meta_tags|safe`, `seo.json_ld|safe`): canonical URL, OG/Twitter tags, JSON-LD.
- `helpers/images.py` — Sanity CDN image URL builder (width/height/quality/format/fit/crop); accepts a plain URL string, an asset `_ref`, or a dict with `url`.
- `helpers/slug.py` — slug extraction + URL builders (`work_url`, `resource_url`, `interview_url`).

**Templates:** every page extends `templates/base.html` (head/SEO tags, nav, mobile menu, footer, scroll-reveal). `templates/macros.html` holds reusable structural pieces (`hero()`, `cta_footer()`, `belongs()`, `menu_link()`, `deliverable()`, etc.) — use these instead of duplicating markup for a new page.

**Sitemap extension model:** `builders/sitemap.py` has no hardcoded per-section knowledge. Each registered `SectionBuilder` contributes its own URLs via `sitemap_entries()`; legacy posts/resources/interviews are passed in separately via `legacy_entries`. Adding a section to `build.py`'s `section_builders` list is the only change needed — the sitemap itself never changes.

**Backward compatibility for Work:** static case-study pages under `pages/work/*.html` (listed in `PAGES` in `builders/pages.py`) are migrated to Sanity one at a time. Migration path: create the `workProject` document in Sanity → verify `/work/{slug}/` renders correctly from CMS → delete the static template → remove its `PAGES` entry. `pages/work/overview.html` is intentionally *not* in `PAGES` since `/work/` is fully CMS-generated by `WorkBuilder`.

**Local dev server** (`builders/server.py`) uses a custom `RangeHTTPRequestHandler` because Python's stock `http.server` ignores HTTP Range requests, which breaks `<video>`/`<audio>` playback. Needed for the home page's hero video.

**JavaScript policy:** JS never stores content, fetches data, or builds markup from data (no `innerHTML` construction, no hardcoded content arrays). All content rendering is server-side (Python/Jinja2). JS only reads `data-*` attributes already emitted by templates (e.g. Work index category filtering) and wires up presentation interactions (slider drag/arrows, nav scroll state, mobile menu). See `CHANGELOG.md` for a real incident where JS violating this policy (`innerHTML = ''` wiping Jinja-rendered content) was fixed — treat that pattern as a hard warning sign in review.

**Sanity Studio** (`studio/`) is a separate TypeScript/Node project defining CMS schemas (`studio/schemaTypes/*.ts`) — `work.ts`, `post.ts`, `resource.ts`, `interview.ts`, `author.ts`, `category.ts`, `blockContent.ts`, `settings.ts`. It doesn't affect the Python build directly; it defines the shape of data `helpers/sanity.py` queries.

## Deployment

Push to `main` → Vercel runs `installCommand` (`pip install --break-system-packages -r requirements.txt`) → `buildCommand` (`python build.py`) → serves `outputDirectory: dist`. A Sanity webhook on `document.publish` can trigger redeploys; no code changes needed for that.
