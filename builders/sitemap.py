"""
builders/sitemap.py — XML sitemap generator.

Generates a standards-compliant sitemap.xml covering every URL the
build pipeline produces.

Extension model
---------------
The sitemap does not hardcode knowledge of individual sections.  Instead,
any SectionBuilder subclass that is registered in ``build.py`` contributes
its own entries via ``SectionBuilder.sitemap_entries()``.  Adding a new
section (Events, Podcasts, …) automatically adds its URLs to the sitemap
with no changes here.

Static pages (builders/pages.py PAGES manifest) are always included.
Legacy dynamic content that still uses builders/posts.py (posts,
resources, interviews) is handled in the ``legacy_entries`` parameter
until it is migrated to the SectionBuilder pattern.

References
----------
- https://www.sitemaps.org/protocol.html
"""

import logging
import os
from datetime import datetime, timezone
from typing import Any
from xml.sax.saxutils import escape as xml_escape

from config import DIST_DIR, SITE_URL
from builders.pages import PAGES
from builders.base import SectionBuilder
from helpers.slug import get_slug

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_HIGH_PRIORITY_PATHS = {
    "", "work", "about", "lets-talk",
    "edtech-mentor-interviews", "resources",
}


def _priority(url_path: str) -> str:
    if url_path in _HIGH_PRIORITY_PATHS:
        return "1.0"
    if url_path.count("/") == 0:
        return "0.9"
    return "0.7"


def _changefreq(url_path: str) -> str:
    if url_path in ("", "work"):
        return "weekly"
    if url_path.startswith("resources/") or url_path.startswith("edtech-mentor"):
        return "monthly"
    return "yearly"


def _url_entry(
    loc: str,
    lastmod: str | None = None,
    changefreq: str = "monthly",
    priority: str = "0.7",
) -> str:
    lines = ["  <url>", f"    <loc>{xml_escape(loc)}</loc>"]
    if lastmod:
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
    lines += [
        f"    <changefreq>{changefreq}</changefreq>",
        f"    <priority>{priority}</priority>",
        "  </url>",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_sitemap(
    section_builders: list[tuple[SectionBuilder, list[dict[str, Any]]]] | None = None,
    legacy_entries:   dict[str, list[dict[str, Any]]] | None = None,
) -> None:
    """
    Write dist/sitemap.xml.

    Parameters
    ----------
    section_builders:
        List of (builder_instance, items) tuples.  Each builder contributes
        its own URLs via ``SectionBuilder.sitemap_entries()``.

    legacy_entries:
        Dict of content-type → item-list for legacy builders that have
        not yet been migrated to SectionBuilder.  Supported keys:

            "posts"      → /resources/{slug}/    (monthly, 0.8)
            "resources"  → /resources/{slug}/    (yearly,  0.7)
            "interviews" → /edtech-mentor-interviews/{slug}/  (yearly, 0.7)
    """
    section_builders = section_builders or []
    legacy_entries   = legacy_entries   or {}

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    entries: list[str] = []
    total = 0

    # ── Static pages from PAGES manifest ────────────────────────────────
    for _template, url_path in PAGES:
        loc = f"{SITE_URL}/{url_path}/" if url_path else f"{SITE_URL}/"
        entries.append(_url_entry(
            loc=loc,
            lastmod=today,
            changefreq=_changefreq(url_path),
            priority=_priority(url_path),
        ))
        total += 1

    # ── SectionBuilder sections ──────────────────────────────────────────
    for builder, items in section_builders:
        for loc, lastmod, changefreq, priority in builder.sitemap_entries(items, today):
            entries.append(_url_entry(loc=loc, lastmod=lastmod,
                                      changefreq=changefreq, priority=priority))
            total += 1

    # ── Legacy: posts → /resources/{slug}/ ──────────────────────────────
    for post in legacy_entries.get("posts", []):
        slug = get_slug(post.get("slug"))
        if not slug:
            continue
        lastmod = (post.get("publishedAt") or today)[:10]
        entries.append(_url_entry(
            loc=f"{SITE_URL}/resources/{slug}/",
            lastmod=lastmod,
            changefreq="monthly",
            priority="0.8",
        ))
        total += 1

    # ── Legacy: resources → /resources/{slug}/ ──────────────────────────
    for resource in legacy_entries.get("resources", []):
        slug = get_slug(resource.get("slug"))
        if not slug:
            continue
        entries.append(_url_entry(
            loc=f"{SITE_URL}/resources/{slug}/",
            lastmod=today,
            changefreq="yearly",
            priority="0.7",
        ))
        total += 1

    # ── Legacy: interviews → /edtech-mentor-interviews/{slug}/ ──────────
    for interview in legacy_entries.get("interviews", []):
        slug = get_slug(interview.get("slug"))
        if not slug:
            continue
        entries.append(_url_entry(
            loc=f"{SITE_URL}/edtech-mentor-interviews/{slug}/",
            lastmod=today,
            changefreq="yearly",
            priority="0.7",
        ))
        total += 1

    # ── Assemble ─────────────────────────────────────────────────────────
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )

    out_path = os.path.join(DIST_DIR, "sitemap.xml")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(xml)

    logger.info("  built /sitemap.xml (%d URLs)", total)
