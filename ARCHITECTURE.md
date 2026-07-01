# 27zero Website — Architecture Reference

This document explains how the project is structured, why each module
exists, and exactly what a developer needs to do to add a new CMS section.
It is meant to be complete enough that a new engineer can continue the
project without asking questions.

---

## Stack

| Layer | Technology |
|-------|-----------|
| CMS | Sanity (GROQ queries, Portable Text) |
| Build | Python 3.11+ |
| Templates | Jinja2 |
| Output | Static HTML in `dist/` |
| Hosting | Vercel (serves `dist/` directly) |
| Fonts | Google Fonts (Lora) |
| CSS | Single file: `assets/css/style.css` |
| JS | Vanilla, presentation-only |

There is no React, no Next.js, no runtime server.  Vercel receives the
`dist/` folder and serves it as static files.

---

## Why this architecture

The project started as a 350-line monolithic `build.py`.  As it grew to
cover Work, Interviews, Resources, and Posts, the pattern of "fetch →
enrich → render → write" was repeated for each section with subtle
differences.  Each repetition was a new place to introduce bugs and a new
file an engineer had to update when the pattern changed.

The refactored architecture extracts the invariant parts of that pattern
into `builders/base.py` (SectionBuilder) and keeps only the section-specific
parts in each section's own file (`builders/work.py`, and future sections).

The result: adding a new CMS section requires writing ~60 lines of
section-specific Python, no changes to any shared infrastructure file.

---

## Directory structure

```
27zero/
│
├── build.py                  ← Orchestrator.  Calls helpers and builders.
├── config.py                 ← All constants and environment variables.
├── requirements.txt          ← Pinned Python dependencies.
├── vercel.json               ← Vercel: buildCommand, outputDirectory.
├── ARCHITECTURE.md           ← This file.
│
├── helpers/                  ← Pure functions.  No side effects.  No file I/O.
│   ├── sanity.py             ← Fetches documents from the Sanity API.
│   ├── portable_text.py      ← Converts Sanity Portable Text → HTML.
│   ├── seo.py                ← Builds canonical/OG/Twitter/JSON-LD context dicts.
│   ├── images.py             ← Builds Sanity CDN image URLs.
│   └── slug.py               ← Slug extraction and URL construction utilities.
│
├── builders/                 ← Write files to dist/.  One module per concern.
│   ├── base.py               ← SectionBuilder base class (the reusable engine).
│   ├── work.py               ← WorkBuilder (reference implementation).
│   ├── pages.py              ← Renders the static-page PAGES manifest.
│   ├── posts.py              ← Legacy builder for posts/resources/interviews.
│   ├── sitemap.py            ← Generates dist/sitemap.xml.
│   ├── rss.py                ← Generates dist/rss.xml.
│   └── server.py             ← Local dev server with HTTP Range support.
│
├── pages/                    ← Jinja2 source templates, one folder per section.
│   ├── home/index.html
│   ├── work/index.html       ← CMS-driven Work index template.
│   ├── work/detail.html      ← CMS-driven Work detail template.
│   ├── work/*.html           ← Static work pages (being migrated to CMS).
│   ├── resources/*.html
│   ├── edtech-marketing/*.html
│   ├── edtech-mentor/*.html
│   ├── about/overview.html
│   └── lets-talk/overview.html
│
├── templates/                ← Shared Jinja2 layout and macros.
│   ├── base.html             ← <head>, nav, footer, scroll-reveal JS.
│   └── macros.html           ← hero(), cta_footer(), belongs(), etc.
│
├── assets/                   ← Static files copied verbatim into dist/.
│   ├── css/style.css
│   ├── images/
│   ├── videos/
│   └── robots.txt
│
└── studio/                   ← Sanity Studio (TypeScript).
    └── schemaTypes/
        ├── work.ts           ← workProject document type.
        ├── post.ts           ← Unified content document type.
        ├── author.ts
        ├── category.ts
        ├── blockContent.ts
        └── settings.ts
```

---

## Module responsibilities

### `config.py`

Single source of truth for every constant in the project.  Reads from
environment variables with hardcoded fallbacks so the project runs locally
without a `.env` file.

```
SITE_URL        — https://www.27zero.agency (override with env var)
DIST_DIR        — absolute path to dist/
PAGES_DIR       — absolute path to pages/
TEMPLATES_DIR   — absolute path to templates/
ASSETS_DIR      — absolute path to assets/
SANITY_*        — project ID, dataset, API URL, CDN URL
VERBOSE         — enables debug logging
```

Nothing else imports directly from Sanity or touches paths.
Everything uses config constants.

---

### `helpers/sanity.py`

All Sanity API interaction lives here.  Every other module that needs CMS
data imports from this file.  It never writes files.

Exports one `_query(groq)` internal function and one public function per
document type:

```python
get_posts()            → list[dict]
get_resources()        → list[dict]
get_interviews()       → list[dict]
get_work_projects()    → list[dict]   # full projection for detail pages
get_work_categories()  → list[str]    # distinct category values
get_settings()         → dict         # global Settings singleton
```

Each function contains a GROQ projection constant and returns the result
array from the Sanity Content Query API.

**Adding a new content type:** add a projection constant and a function.
Nothing else changes.

---

### `helpers/portable_text.py`

Converts Sanity Portable Text block arrays into HTML strings.  Called by
subclasses of SectionBuilder in their `body_html()` method, and by
`builders/posts.py` for legacy builders.

Handles: H1–H6, paragraphs, blockquote, bullet lists, ordered lists,
strong, em, underline, strike-through, code, links (external links get
`target="_blank"`), images.

Unknown block types emit an HTML comment so editors can spot gaps during
QA without the page breaking.

---

### `helpers/seo.py`

Builds a complete SEO context dict from a set of parameters.  Called by
every builder.  Returns a dict with:

```
canonical   — absolute canonical URL
description — resolved meta description
meta_tags   — HTML string: OG, Twitter Card tags
json_ld     — HTML <script> tag: Organization + WebSite + WebPage + Article + BreadcrumbList
```

Templates consume this as `{{ seo.meta_tags|safe }}` and `{{ seo.json_ld|safe }}`.
The SEO logic lives here once.  No builder duplicates it.

---

### `helpers/images.py`

Builds Sanity CDN URLs with optional width, height, quality, format, fit,
and crop parameters.

```python
image_url(source, width=800, auto="format")
responsive_srcset(source, [400, 800, 1200])
```

`source` can be a plain string URL, a Sanity asset `_ref`, or a dict with
a `"url"` key.  All shapes are handled transparently.

---

### `helpers/slug.py`

Small utilities for working with Sanity slug fields:

```python
get_slug(slug_field)   — extracts string from {current: "slug"} objects
slugify(text)          — converts arbitrary text to a URL-safe slug
work_url(slug)         → "/work/{slug}/"
resource_url(slug)     → "/resources/{slug}/"
interview_url(slug)    → "/edtech-mentor-interviews/{slug}/"
```

---

### `builders/base.py` — SectionBuilder

The core abstraction.  Every CMS-driven section is a subclass of
`SectionBuilder`.

**Responsibilities:**
- Build loop: index page + one detail page per item
- Item enrichment: resolved image URLs, category labels, gallery src URLs
- Related-item scoring: same category (+2) + shared services (+1 each)
- Category grouping for filter tabs
- SEO context construction (delegates to `helpers/seo.py`)
- Template loading and rendering (via Jinja2 Environment)
- File writing: `dist/{section}/index.html` and `dist/{section}/{slug}/index.html`
- Sitemap entry generation (yields tuples consumed by `builders/sitemap.py`)
- Error handling: template not found and render errors log and continue

**Why one class, not four modules?**

The natural decomposition would be: `filesystem.py` for writes,
`renderer.py` for rendering, a `seo.py` builder for SEO, `registry.py`
for sitemap registration.

This was evaluated and rejected.  Every method in SectionBuilder reads
instance state: `self.section`, `self.category_key`, `self.THUMB_WIDTH`,
`self.label_map`.  Extracting them into free functions requires passing
that state as parameters on every call, or making the functions depend
on the class again.  The result is four files that are more tightly
coupled than the current one.

The Single Responsibility Principle is about *reasons to change*, not
file count.  SectionBuilder changes when the section-building algorithm
changes.  That is one reason.

**Extension surface — what subclasses override:**

| Method | Purpose | Required? |
|--------|---------|-----------|
| `enrich_item(item)` | Add resolved URLs, computed strings | No — base adds thumbnailUrl, heroUrl, categoryLabel |
| `body_html(item)` | Render portable-text fields → HTML dict | No — base returns `{}` |
| `index_context(...)` | Template variable mapping for index | No — base provides `items`, `categories`, `items_by_category`, `featured`, `seo` |
| `detail_context(...)` | Template variable mapping for detail | No — base provides `item`, `body_html`, `related`, `gallery`, `seo` |
| `detail_seo(item, slug)` | SEO title, og_type, breadcrumbs | No — base builds `{title} — 27zero` + Article schema |
| `sitemap_entries(items, today)` | Sitemap priority, changefreq | No — base yields index + details with sensible defaults |

---

### `builders/work.py` — WorkBuilder

The reference implementation.  Study this file before building the next
section.

Extends SectionBuilder with:

1. **Class attributes** — section name, Sanity type, index title and
   description, category key, services key for related scoring,
   category label map.

2. **`body_html()`** — renders the two portable-text fields used by the
   Work detail template: `challenge` and `solution.body`.

3. **`index_context()`** — adds `projects` and `projects_by_category`
   as aliases for `items` and `items_by_category`.  The Work templates
   were written before the generic naming convention was established;
   the aliases maintain backward compatibility without changing the
   templates.

4. **`detail_context()`** — adds `project` as an alias for `item`.

Module-level `build_work(env, projects)` is a thin wrapper kept for
readability at the call site in `build.py`.

---

### `builders/pages.py`

Renders every entry in the `PAGES` manifest — the list of
`(template_path, url_path)` tuples for pages whose content does not come
from Sanity.

Every template receives `posts`, `resources`, `work`, and `seo` context
so any static page can display dynamic CMS content (e.g. the homepage
shows recent resources).

**Work index note:** `"work/overview.html"` / `"work"` is intentionally
absent from PAGES.  `/work/` is now generated by `WorkBuilder`.
The individual static work case-study pages remain in PAGES until their
content has been migrated to Sanity.

---

### `builders/posts.py`

Legacy builder for posts, resources, and interviews.  Predates
SectionBuilder.  Continues to work unchanged.

When the templates for these sections are redesigned, migrate them to
SectionBuilder subclasses and remove the corresponding functions from
this file.

---

### `builders/sitemap.py`

Generates `dist/sitemap.xml`.

**Extension model:** the sitemap does not contain hardcoded knowledge of
individual sections.  Instead, each `SectionBuilder` registered in
`build.py` contributes its own entries via `sitemap_entries()`.  Adding
a new section to `build.py` automatically adds its URLs to the sitemap
with no changes here.

Legacy content (posts, resources, interviews) that still uses
`builders/posts.py` is handled via the `legacy_entries` parameter until
it is migrated to SectionBuilder.

**Why the registry pattern instead of the old keyword-argument API?**

The old API was `build_sitemap(posts=, resources=, interviews=, work=)`.
Each new section required: (a) adding a parameter to `build_sitemap`, and
(b) adding a `for item in section` loop inside the function.  The sitemap
was a closed extension point.

The new API is `build_sitemap(section_builders=[(builder, items)], legacy_entries={...})`.
Adding a new section requires only one change: appending to
`section_builders` in `build.py`.  The sitemap itself never changes.

---

### `builders/rss.py`

Generates `dist/rss.xml`.  Currently covers posts and resources.
Linked from `<head>` in `templates/base.html` for RSS autodiscovery.

---

### `builders/server.py`

Local development HTTP server that handles HTTP Range requests correctly.
Python's built-in `http.server` ignores Range headers, which prevents
`<video>` elements from loading.  This custom handler supports byte-range
serving so video playback works during local development.

Usage: `python build.py serve` or `python build.py serve 3000`

---

### `templates/base.html`

Shared Jinja2 layout extended by every page.

Contains:
- `<head>` with canonical, meta description, OG/Twitter tags, JSON-LD
  (all from the `seo` context dict)
- RSS autodiscovery link
- Navigation (sticky white → purple pill on scroll)
- Mobile menu (hamburger, overlay, keyboard and Escape handling)
- Footer (large nav rows with hover-black effect, social link)
- Scroll-reveal IntersectionObserver
- `{% block content %}` — overridden by each page

---

### `templates/macros.html`

Jinja2 macros for structural components reused across many pages:

```
hero(eyebrow, href, title_html, subtitle, large, micro, narrow)
cta_footer(title_html, large, narrow)
belongs(text, href)        — breadcrumb back-link
menu_link(href, label, desc)  — dark service menu card
sub_link(href, label)      — dark service sub-row
deliverable(title, desc)   — ditem card
proof_point(text)          — callout block
```

---

### `studio/schemaTypes/work.ts`

Sanity document type for Work / Case Study projects.

Fields are grouped into five tabs in the Studio UI:
- **Overview** — title, slug, client, logo, category, services, industry, year, excerpt
- **Case Study** — brief (text), challenge (blockContent), solution (object: headline + blockContent), impact (array of {verb, result} pairs)
- **Media** — thumbnail, heroImage, heroVideo URL, gallery
- **SEO** — seoTitle, seoDescription, ogImage
- **Metadata** — featured (boolean), order (integer)

The `impact` field is a structured `{verb, result}` array rather than
free text so the template can render the `look-item` layout
(`<h3>Fueled</h3><p>The sales cycle…</p>`) without string parsing.

---

## Data flow

```
Sanity Content Lake
      │
      │  GROQ queries (helpers/sanity.py)
      ▼
Raw document dicts
      │
      │  Enrichment (SectionBuilder.enrich_item)
      │    - Resolves image URLs via helpers/images.py
      │    - Adds computed labels via label_map
      │
      │  Portable Text rendering (SectionBuilder.body_html → subclass)
      │    - helpers/portable_text.py → HTML strings
      │
      │  SEO context (SectionBuilder.detail_seo → helpers/seo.py)
      │    - canonical URL
      │    - OG / Twitter meta tags
      │    - JSON-LD structured data
      │
      │  Related scoring (SectionBuilder._related)
      │    - same category (+2) + shared services (+1)
      │
      │  Category grouping (SectionBuilder._group_by)
      │    - for filter tabs on index pages
      ▼
Jinja2 template context dict
      │
      │  template.render(**ctx)  via Jinja2 Environment
      ▼
HTML string
      │
      │  SectionBuilder._write()
      ▼
dist/{section}/index.html
dist/{section}/{slug}/index.html
```

---

## Build flow

```
python build.py
      │
      ├── Step 1: Fetch from Sanity
      │     get_posts(), get_resources(), get_interviews(), get_work_projects()
      │     ↳ All fetches complete before dist/ is touched.
      │       Any failure here aborts cleanly.
      │
      ├── Step 2: Clear dist/
      │
      ├── Step 3: Configure Jinja2 Environment
      │     FileSystemLoader([pages/, templates/])
      │
      ├── Step 4: Static pages
      │     builders/pages.py → PAGES manifest → dist/
      │
      ├── Step 5: Legacy CMS builders
      │     builders/posts.py → dist/resources/{slug}/
      │     builders/posts.py → dist/edtech-mentor-interviews/{slug}/
      │
      ├── Step 6: SectionBuilder sections
      │     WorkBuilder().build(env, work)
      │       → dist/work/index.html
      │       → dist/work/{slug}/index.html  (one per project)
      │
      ├── Step 7: Sitemap
      │     builders/sitemap.py
      │       → PAGES manifest entries
      │       → SectionBuilder.sitemap_entries() for each registered builder
      │       → Legacy posts/resources/interviews entries
      │       → dist/sitemap.xml
      │
      ├── Step 8: RSS
      │     builders/rss.py → dist/rss.xml
      │
      └── Step 9: Copy assets
            assets/ → dist/assets/
```

---

## How to add a new CMS section

The complete list of steps.  Each step is small and isolated.

### Step 1 — Sanity schema

Create `studio/schemaTypes/{section}.ts` (copy `work.ts` as a starting
point, adjust fields).  Register it in `studio/schemaTypes/index.ts`.

### Step 2 — GROQ query

Add a projection constant and a `get_{section}()` function to
`helpers/sanity.py`.  Follow the pattern of `_WORK_DETAIL_PROJECTION`
and `get_work_projects()`.

### Step 3 — Builder

Create `builders/{section}.py`:

```python
from typing import Any
from builders.base import SectionBuilder
from helpers.portable_text import render_portable_text  # only if needed

class PodcastsBuilder(SectionBuilder):

    # Required
    section     = "podcasts"
    sanity_type = "podcast"

    # Recommended
    index_title = "Podcasts — EdTech Conversations — 27zero"
    index_desc  = "Long-form audio conversations with EdTech leaders."

    # Optional — only if your category field uses different values
    category_key = "series"
    label_map = {
        "founders":  "Founders Series",
        "investors": "Investor Series",
    }

    # Optional — only if you have portable-text fields
    def body_html(self, item: dict[str, Any]) -> dict[str, str]:
        return {
            "description": render_portable_text(item.get("description") or []),
        }


def build_podcasts(env, podcasts: list[dict[str, Any]]) -> int:
    return PodcastsBuilder().build(env, podcasts)
```

If your templates use section-specific variable names (e.g. `podcast`
instead of `item`), override `detail_context()` to add aliases:

```python
def detail_context(self, item, body_html, related, gallery, seo):
    ctx = super().detail_context(item, body_html, related, gallery, seo)
    return {**ctx, "podcast": item}
```

### Step 4 — Templates

Create `pages/{section}/index.html` and `pages/{section}/detail.html`.
Both should `{% extends "base.html" %}`.

The index template receives: `items`, `categories`, `items_by_category`,
`featured`, `seo`.

The detail template receives: `item`, `body_html`, `related`, `gallery`,
`seo`.

Use the Work templates (`pages/work/index.html`, `pages/work/detail.html`)
as a reference.

### Step 5 — Wire into build.py

Add three lines to the `build()` function:

```python
# In the fetch block (Step 1):
podcasts = get_podcasts()

# In the SectionBuilder block (Step 6):
podcasts_builder = PodcastsBuilder()
n_podcasts = podcasts_builder.build(env, podcasts)

# In section_builders (Step 7):
section_builders = [
    (work_builder, work),
    (podcasts_builder, podcasts),  # add this line
]
```

Sitemap entries are automatic.  SEO is automatic.  No other file changes.

### Step 6 — Sanity content

Publish documents in the Sanity Studio.  Trigger a Vercel deploy (or
wait for the webhook).

---

## JavaScript policy

JavaScript in this project is **presentation-only**.  It is responsible
for:

- Navigation scroll behaviour (sticky nav → purple pill)
- Mobile menu open/close (hamburger, overlay, Escape key, focus management)
- Scroll-reveal animation (IntersectionObserver)
- Work index filtering (show/hide cards by `data-category` attribute)
- Video autoplay pause for `prefers-reduced-motion`

JavaScript is **never** responsible for:

- Storing content (no `const CATEGORIES = [...]`)
- Fetching data (no API calls at runtime)
- Rendering markup (no `innerHTML` construction from data)

All content is rendered server-side by Python and Jinja2.  The
`data-category` attributes on Work cards are emitted by Jinja2.
JavaScript only reads those attributes to show/hide cards — it never
knows what the categories are.

---

## Backward compatibility

**Existing URLs are permanent.**  The static work detail pages
(`/work/anthology-legacy-conversations/`, `/work/student-first/`, etc.)
continue to be built from `pages/work/*.html` via `builders/pages.py`
until their content is migrated to Sanity.

**Migration path for static work pages:**

1. Create the corresponding `workProject` document in Sanity.
2. Fill all fields from the static page content.
3. Verify that `/work/{slug}/` renders correctly from the CMS.
4. Delete the static file from `pages/work/`.
5. Remove its entry from `PAGES` in `builders/pages.py`.

The CMS-generated detail page takes over the URL transparently.

---

## Environment variables

Set these in Vercel project settings for production:

| Variable | Purpose | Default |
|----------|---------|---------|
| `SITE_URL` | Canonical base URL | `https://www.27zero.agency` |
| `SANITY_PROJECT_ID` | Sanity project identifier | `qjn4zzjc` |
| `SANITY_DATASET` | Sanity dataset name | `production` |
| `SANITY_TOKEN` | API token for private/draft content | `""` |
| `DRAFT_MODE` | Include draft documents | `false` |
| `VERBOSE` | Debug-level build logging | `false` |

The hardcoded fallbacks in `config.py` allow local development without
creating a `.env` file.

---

## Deployment

```
git push origin main
      │
      ▼
Vercel detects push
      │
      ▼
installCommand: python -m pip install --break-system-packages -r requirements.txt
      │
      ▼
buildCommand: python build.py
      ▼
outputDirectory: dist/
      │
      ▼
Vercel deploys dist/ as static files
```

For automatic deploys on Sanity publish events: configure a Sanity webhook
pointing at the Vercel Deploy Hook URL.  Set the webhook to fire on
`document.publish`.  No code changes are required.
