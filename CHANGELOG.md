# CHANGELOG

## Fix: Work page JS no longer overwrites Jinja-rendered HTML

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
