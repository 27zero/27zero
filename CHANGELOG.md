# CHANGELOG — Work asset pipeline fix

## Problem

`dist/work/style.css` and `dist/work/script.js` were committed directly inside
`dist/`. `build.py` runs `shutil.rmtree(DIST_DIR)` on every build, deleting
both files permanently. After every build the Work page loaded with no CSS
and no JS.

---

## Files modified

### 1. `assets/css/work.css` — CREATED (new file)

- **Content:** exact copy of `dist/work/style.css`, zero modifications.
- **Why:** Files in `assets/` are copied to `dist/assets/` by the existing
  `shutil.copytree(ASSETS_DIR, dist/assets/)` step in `build.py` (step 9).
  Moving the CSS here means it survives every build with no pipeline changes.

### 2. `assets/js/work.js` — CREATED (new file)

- **Content:** exact copy of `dist/work/script.js`, zero modifications.
- **Why:** Same reason as `work.css`.

### 3. `pages/work/index.html` — MODIFIED

The Jinja template for the Work index page was accidentally committed in
`dist/work/index.html` (279 lines, 21 Jinja tags). `pages/work/index.html`
contained a 422-line static HTML snapshot with 0 Jinja tags — not a template.
`WorkBuilder` renders `pages/work/index.html` via `section="work"`.

The template from `dist/work/index.html` is moved to `pages/work/index.html`
with five line-level fixes only. Nothing else changed.

| Line (original) | Change | Reason |
|---|---|---|
| 2 | `{% from "ma}cros.html" import cta_footer %` → `{% from "macros.html" import cta_footer %}` | Typo `ma}cros` + missing `%}` closing tag → Jinja raises `expected token 'end of statement block'`, build fails |
| 10 | `href="/dist/work/style.css"` → `href="/assets/css/work.css"` | `/dist/work/` is deleted on every build |
| 102–104 | Three lines removed: `<!-- {% for project in projects %}`, blank, `{% if project.category == category.value %} -->` | Jinja parses `{% %}` inside HTML comments. Orphaned `{% if %}` causes `Encountered unknown tag 'endif'`, build fails |
| 204–205 | Two lines removed: `<!-- {% endif %} -->`, blank | Matching orphaned `{% endif %}` inside HTML comment, same nesting error |
| 277→272 | `src="/dist/work/script.js"` → `src="/assets/js/work.js"` | `/dist/work/` is deleted on every build |

---

## Files NOT modified

Every other file in the repository is byte-for-byte identical to the
original clone from `https://github.com/27zero/27zero.git` (commit `f87764e`):

- `build.py`
- `config.py`
- `builders/base.py`, `builders/work.py`, `builders/pages.py`,
  `builders/posts.py`, `builders/sitemap.py`, `builders/rss.py`,
  `builders/server.py`, `builders/__init__.py`
- `helpers/sanity.py`, `helpers/portable_text.py`, `helpers/seo.py`,
  `helpers/images.py`, `helpers/slug.py`, `helpers/__init__.py`
- `templates/base.html`, `templates/macros.html`
- `pages/work/overview.html`, `pages/work/detail.html`
- All other files in `pages/`
- `assets/css/style.css`, `assets/robots.txt`
- `assets/images/`, `assets/videos/`
- `studio/` (all schema files)
- `vercel.json`, `requirements.txt`, `README.md`, `ARCHITECTURE.md`
- All files in `dist/`

---

## How to use

Decompress the ZIP. Run:

```
python build.py
```

`work.css` and `work.js` will be copied to `dist/assets/` automatically
by the existing pipeline.
