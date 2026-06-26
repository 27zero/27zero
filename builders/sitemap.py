"""
builders/sitemap.py — XML sitemap generator.

Generates a standards-compliant sitemap.xml that includes every page
built by the static builder plus every dynamically generated post,
resource, and interview page.

The sitemap is written to dist/sitemap.xml and referenced in robots.txt.

References
----------
- https://www.sitemaps.org/protocol.html
- https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap
"""

import logging
import os
from datetime import datetime, timezone
from typing import Any
from xml.sax.saxutils import escape as xml_escape

from config import DIST_DIR, SITE_URL
from builders.pages import PAGES
from helpers.slug import get_slug

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Priority and change-frequency heuristics
# ---------------------------------------------------------------------------

# Pages that deserve higher crawl priority.
_HIGH_PRIORITY_PATHS = {"", "work", "about", "lets-talk", "edtech-mentor-interviews", "resources"}


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


def _url_entry(loc: str, lastmod: str | None = None,
               changefreq: str = "monthly", priority: str = "0.7") -> str:
    lines = [f"  <url>", f"    <loc>{xml_escape(loc)}</loc>"]
    if lastmod:
        lines.append(f"    <lastmod>{lastmod}</lastmod>")
    lines += [
        f"    <changefreq>{changefreq}</changefreq>",
        f"    <priority>{priority}</priority>",
        f"  </url>",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_sitemap(
    posts: list[dict[str, Any]] | None = None,
    resources: list[dict[str, Any]] | None = None,
    interviews: list[dict[str, Any]] | None = None,
) -> None:
    """
    Write dist/sitemap.xml.

    Includes:
    - All static pages from builders/pages.py PAGES manifest
    - One entry per published post
    - One entry per published resource
    - One entry per published interview
    """
    posts      = posts or []
    resources  = resources or []
    interviews = interviews or []

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    entries: list[str] = []

    # ── Static pages ────────────────────────────────────────────────────
    for _template, url_path in PAGES:
        loc = f"{SITE_URL}/{url_path}/" if url_path else f"{SITE_URL}/"
        entries.append(_url_entry(
            loc=loc,
            lastmod=today,
            changefreq=_changefreq(url_path),
            priority=_priority(url_path),
        ))

    # ── Posts ────────────────────────────────────────────────────────────
    for post in posts:
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

    # ── Resources ────────────────────────────────────────────────────────
    for resource in resources:
        slug = get_slug(resource.get("slug"))
        if not slug:
            continue
        entries.append(_url_entry(
            loc=f"{SITE_URL}/resources/{slug}/",
            lastmod=today,
            changefreq="yearly",
            priority="0.7",
        ))

    # ── Interviews ───────────────────────────────────────────────────────
    for interview in interviews:
        slug = get_slug(interview.get("slug"))
        if not slug:
            continue
        entries.append(_url_entry(
            loc=f"{SITE_URL}/edtech-mentor-interviews/{slug}/",
            lastmod=today,
            changefreq="yearly",
            priority="0.7",
        ))

    # ── Assemble XML ─────────────────────────────────────────────────────
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )

    out_path = os.path.join(DIST_DIR, "sitemap.xml")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(xml)

    total = len(PAGES) + len(posts) + len(resources) + len(interviews)
    logger.info("  built /sitemap.xml (%d URLs)", total)
