#!/usr/bin/env python3
"""
scripts/reconcile_mentors.py — Sanity ↔ generated-HTML reconciliation for
The EdTech Mentor interviews.

Run this wherever the sandbox actually has network access to Sanity and a
valid SANITY_TOKEN (if drafts/private dataset access is needed) — e.g. a
local machine, CI, or a Vercel preview shell. It requires no code changes
to the site itself; it imports the exact same helpers/builders build.py
uses, so there is no risk of it drifting from production behaviour.

What it does
------------
1. Calls helpers.sanity.get_mentor_interviews() — the exact same GROQ
   query build.py uses — and prints Title / Series / Slug / Published /
   Featured for every document, straight from the dataset.
2. Builds the real EdTech Mentor index page with MentorBuilder (same code
   path as a real `python build.py` run) into a temp directory, so the
   comparison is against genuinely generated HTML, not a guess.
3. Parses that HTML for every interview slug that actually appears in a
   rendered card (featured card + all three series sliders).
4. Diffs the two lists and prints, for every document NOT rendered, the
   exact reason: missing slug (excluded by the GROQ query itself before
   this script even sees it — reported separately), missing series value,
   or a series value that doesn't match any of the three known keys.

Usage
-----
    cd /path/to/27zero
    python scripts/reconcile_mentors.py

Exit code is 0 if every fetched document is accounted for in the
rendered HTML, 1 otherwise (so this can be wired into CI).
"""

import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jinja2 import Environment, FileSystemLoader

from config import PAGES_DIR, TEMPLATES_DIR
from helpers.sanity import get_mentor_interviews
from builders.mentor import MentorBuilder, SERIES_CONFIG

KNOWN_SERIES_KEYS = {s["key"] for s in SERIES_CONFIG}


def fetch_and_print() -> list[dict]:
    """Fetch the live dataset and print Title/Series/Slug/Published/Featured."""
    interviews = get_mentor_interviews()

    print("\n=== Mentor Interviews — raw from Sanity ===")
    if not interviews:
        print("(0 documents returned — check SANITY_TOKEN / network access "
              "before trusting any conclusion below)")
    for it in interviews:
        print({
            "title":       it.get("title") or it.get("guestName"),
            "series":      it.get("series"),
            "slug":        it.get("slug"),
            "publishedAt": it.get("publishedAt"),
            "featured":    it.get("featured"),
        })
    print(f"=== {len(interviews)} document(s) returned by get_mentor_interviews() ===\n")
    return interviews


def render_index_html(interviews: list[dict]) -> str:
    """Render the real MentorBuilder index page and return its HTML."""
    env = Environment(loader=FileSystemLoader([PAGES_DIR, TEMPLATES_DIR]))
    builder = MentorBuilder()

    # Reuse the builder's own internals exactly as build() would, but
    # capture the rendered HTML instead of only writing it to disk, so we
    # can inspect it directly without depending on other sections' output.
    from helpers.i18n import LOCALES, load_locale, prefix_url

    loc = LOCALES[0]  # en-us / canonical
    template = env.get_template(builder._index_template_name)
    i18n = load_locale(loc["key"])
    localized_url = prefix_url(builder.section, loc["prefix"])

    enriched = [builder.enrich_item(item) for item in interviews]
    groups = builder._group_by(enriched)
    categories = [
        {"value": cat, "label": builder._label(cat), "count": len(grp)}
        for cat, grp in groups.items()
    ]
    featured = [item for item in enriched if item.get("featured")]

    from helpers.seo import build_seo_context
    seo = build_seo_context(
        url_path=localized_url, url_path_neutral=builder.section,
        title=builder.index_title, description=builder.index_desc,
        og_type=builder.index_og_type, locale="en", og_locale="en_US",
        breadcrumbs=[{"name": "Home", "url": "/"},
                     {"name": "Edtech Mentor Interviews", "url": f"/{builder.section}/"}],
    )
    ctx = builder.index_context(items=enriched, categories=categories,
                                 groups=groups, featured=featured, seo=seo)
    ctx.update(builder._shared_context(loc, i18n, builder.section, localized_url, seo))
    return template.render(**ctx)


def rendered_slugs(html: str) -> set[str]:
    """Every /edtech-mentor-interviews/{slug}/ href that appears in a card."""
    return set(re.findall(r'/edtech-mentor-interviews/([^/"\']+)/', html))


def main() -> int:
    interviews = fetch_and_print()
    if not interviews:
        print("Nothing to reconcile — 0 documents fetched. Fix Sanity access "
              "first (see the printed reason above).")
        return 1

    html = render_index_html(interviews)
    rendered = rendered_slugs(html)

    print("=== Reconciliation ===")
    missing = []
    for it in interviews:
        slug = it.get("slug")
        title = it.get("title") or it.get("guestName") or "(untitled)"
        series = it.get("series")

        if not slug:
            missing.append((title, slug, series, "no slug — never reaches the "
                             "template (excluded by the GROQ defined(slug.current) filter "
                             "at the query itself, before HTML is even generated)"))
            continue

        if slug not in rendered:
            if not series:
                reason = "series is empty/None — falls into the unread 'other' bucket"
            elif series not in KNOWN_SERIES_KEYS:
                reason = (f"series={series!r} does not match any of the three "
                          f"known keys {sorted(KNOWN_SERIES_KEYS)} — falls into "
                          f"the unread 'other' bucket")
            else:
                reason = ("series is valid but the document still isn't in the "
                          "rendered HTML — investigate further, this is unexpected")
            missing.append((title, slug, series, reason))

    if not missing:
        print(f"All {len(interviews)} document(s) are accounted for in the "
              f"generated HTML. No reconciliation gaps found.")
        return 0

    print(f"{len(missing)} of {len(interviews)} document(s) are NOT rendered "
          f"anywhere on the EdTech Mentor index page:\n")
    for title, slug, series, reason in missing:
        print(f"  - {title!r} (slug={slug!r}, series={series!r})")
        print(f"      → {reason}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
