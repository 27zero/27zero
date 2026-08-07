# CHANGELOG

## Fix: Essential Series silently disappears + testimonial photo overflows homepage footer section

**Commit base:** HEAD (main)
**Files modified:** builders/base.py, build.py, assets/css/home.css (3 files)

---

### Issue #1 — "Essential Series" interview cards not rendering

**Root cause:** Not a code defect — the GROQ query, `MentorBuilder`, and
`pages/edtech-mentor/index.html` are correctly wired and symmetric across
all three series (confirmed against `studio/27zero-sanity`'s
`schemaTypes/interview.ts`, whose `SERIES_OPTIONS` value `'essencial'`
matches `builders/mentor.py`'s `SERIES_CONFIG` key exactly — same string,
same spelling). Since Investor and Founders cards render fine through this
same `_group_by()` → template-loop path, the pipeline itself is proven to
work. The empty section means no interview document currently resolves
`series` to exactly `"essencial"` — most likely because `series`/
`featured`/`title` are new fields layered onto a pre-existing `interview`
type (see `builders/mentor.py`'s own docstring), and one or more documents
were never given a value for the new field. `SectionBuilder._group_by()`
silently buckets any non-matching value into `"other"`, which the template
never reads — so the failure was invisible anywhere in the pipeline or
build log.

**Fix:** `builders/base.py` — `_group_by()` now logs a warning (item slug/
name + the offending value) whenever a subclass with a `label_map` groups
an item under a key that isn't one of the known keys. Purely additive;
verified byte-identical grouping output for matching items via a
standalone test with 5 sample interviews (3 matching, 1 missing `series`,
1 wrong-case) — the 2 mismatches now print a warning, nothing else changed.

**Also added** (`build.py`, right after `get_mentor_interviews()`): a raw
diagnostic print of `title` / `series` / `slug` / `featured` for every
interview exactly as returned by Sanity, before any enrichment or
grouping — so a mismatched value is visible in the Vercel build log
without needing to compare rendered HTML back to Studio by hand.

---

### Issue #2 — Homepage footer section: illustration overflows its container

**Not in `components/footer/`** — the reported "footer illustration" is
the testimonial photo in `section--testimonials-home`, the actual last
section before the real `<footer>`.

**Root cause:** `assets/css/home.css` was split into its own file in
commit `dac3965`, when the testimonials markup used classes
`.testimonial-slide` / `.testimonial-quote-icon`. Commit `5a06e75`
("Santiago design exact") later rewrote the homepage HTML wholesale and
renamed those elements to `.testimonial-item` / `.testimonial-photo` —
but `assets/css/home.css` was never updated to match. Result:
`.testimonial-photo` and its `<img>` (`t.backgroundPhotoUrl`, a real
Sanity photo) had **zero CSS rules** anywhere in the stylesheet, so the
image rendered at its native intrinsic size instead of being constrained.

Reproduced with Playwright (real Chromium) by rendering the actual Jinja
template with an injected 2400×1600px test photo:
`img` computed `width: 2400px; height: 1600px; max-width: none`;
`.testimonial-photo` / `.testimonial-item` both `2400px` wide,
`overflow: visible`; section height ballooned to ~1950px, saved from a
page-level horizontal scrollbar only because `.testimonials-track-wrap`
has `overflow: hidden`, which silently clipped it instead of containing
it gracefully.

**Fix (`assets/css/home.css`):** extended the two still-present, never-
renamed selectors to also match the current class names — same values,
no redesign:

```css
.testimonial-slide,
.testimonial-item { flex: 0 0 100%; display: flex; justify-content: center;
                     align-items: center; gap: 3em; }

.testimonial-quote-icon,
.testimonial-photo { flex-shrink: 0; width: 30em; height: auto; }

.testimonial-photo img { display: block; width: 100%; height: auto; }
```

Plus the matching mobile rule (`≤768px`) that already hid the icon was
extended to also hide `.testimonial-photo`, unchanged otherwise.

**Verified** with the same Playwright script, before/after:

| | before | after |
|---|---|---|
| desktop 1440px | img `2400×1600px`, `right: 2557` (overflows viewport) | img `420×280px`, `right: 699` (fully inside) |
| tablet 768px | img `2400×1600px` | `display: none` (per existing design) |
| mobile 375px | img `2400×1600px` | `display: none` (per existing design) |
| `document.documentElement.scrollWidth` vs `clientWidth` | equal at all 3 (page-level scroll was already masked by a wrapper's `overflow:hidden`) | equal at all 3, section itself now correctly sized (~213px vs ~1950px before) |

`assets/css/home.css` is linked only from `pages/home/index.html`, and
`.testimonial-item`/`.testimonial-photo`/`.testimonial-slide`/
`.testimonial-quote-icon` aren't used by any other page or component —
change is fully scoped, no other page affected.

---

### Files NOT modified

Every other file is unchanged: config.py, helpers/, templates/, pages/
(except the diagnostic print's call site in build.py), components/,
studio/, vercel.json, requirements.txt.


**Commit base:** f386f07 (origin/main)
**File modified:** assets/js/work.js (1 file, no other changes)

---

### Problem

assets/js/work.js contained a renderAllSliders() function that executed
immediately on page load. Its first action was:

  slidersContainer.innerHTML = '';

This wiped every card and slider block that Python/Jinja had rendered from
real Sanity data, replacing them with hardcoded placeholder content
([PROJECT THUMBNAIL], [Project headline], [CLIENT NAME]) from the
CATEGORIES array.

---

### Lines removed (original lines 5-185)

Lines  5-14   const CATEGORIES = [...]
               Hardcoded data with placeholder category IDs.
               Source of truth is Sanity, rendered by Jinja.

Line   16      const CARDS_PER_CATEGORY = 6
               Only used by createCardElement. Removed with it.

Lines 18-50    function createCardElement()
               Generated placeholder cards with [PROJECT THUMBNAIL], [CLIENT NAME].

Lines 52-105   function createSliderBlock()
               Built slider DOM from scratch, bypassing Jinja output.

Lines 176-185  function renderAllSliders() + renderAllSliders() call
               innerHTML = '' on line 181 destroyed all Jinja-rendered
               content on every page load. Root cause of the bug.

---

### Lines added (replacing lines 176-185)

  // ===== Wire interactions to Jinja-rendered DOM =====

  const slidersContainer = document.getElementById('slidersContainer');

  document.querySelectorAll('.slider-block').forEach(block => {
    const track  = block.querySelector('.slider-track');
    const footer = block.querySelector('.slider-footer');
    if (track)           enableSliderDrag(track);
    if (track && footer) enableSliderArrows(footer, track);
  });

Finds every .slider-block already in the DOM (rendered by Jinja from
Sanity data) and attaches drag and arrow event listeners.
No HTML is created or destroyed.

---

### Code kept exactly as written (no changes)

  function enableSliderDrag()    drag/pointer events on slider track
  function enableSliderArrows()  prev/next arrow navigation and state
  Pills filtering block          show/hide slider blocks by data-category

---

### Files NOT modified

Every other file in the repository is byte-for-byte identical to the
original clone from https://github.com/27zero/27zero.git (f386f07):

build.py, config.py, builders/, helpers/, templates/,
pages/, assets/css/, studio/, vercel.json, requirements.txt
