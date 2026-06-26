"""
builders/rss.py — RSS 2.0 feed generator.

Generates dist/rss.xml containing the most recent posts and resources.
The feed is linked from <head> in base.html so RSS readers can
auto-discover it.

Spec: https://www.rssboard.org/rss-specification
"""

import logging
import os
from datetime import datetime, timezone
from email.utils import format_datetime, parsedate_to_datetime
from typing import Any
from xml.sax.saxutils import escape as xml_escape

from config import DIST_DIR, SITE_URL, RSS_TITLE, RSS_DESCRIPTION, RSS_AUTHOR
from helpers.slug import get_slug

logger = logging.getLogger(__name__)

MAX_ITEMS = 20  # Maximum number of items in the feed.


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _rfc2822(iso: str | None) -> str:
    """Convert an ISO 8601 datetime string to RFC 2822 format for RSS."""
    if iso:
        try:
            dt = parsedate_to_datetime(iso) if "," in iso else datetime.fromisoformat(iso.replace("Z", "+00:00"))
            return format_datetime(dt)
        except Exception:
            pass
    return format_datetime(datetime.now(timezone.utc))


def _item(
    title: str,
    link: str,
    description: str,
    pub_date: str | None,
    author: str | None = None,
) -> str:
    parts = [
        "  <item>",
        f"    <title>{xml_escape(title)}</title>",
        f"    <link>{xml_escape(link)}</link>",
        f"    <guid isPermaLink=\"true\">{xml_escape(link)}</guid>",
        f"    <description>{xml_escape(description)}</description>",
        f"    <pubDate>{_rfc2822(pub_date)}</pubDate>",
    ]
    if author:
        parts.append(f"    <author>{xml_escape(author)}</author>")
    parts.append("  </item>")
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_rss(
    posts: list[dict[str, Any]] | None = None,
    resources: list[dict[str, Any]] | None = None,
) -> None:
    """
    Write dist/rss.xml.

    Combines posts and resources, sorted newest-first (posts have
    publishedAt; resources sort after posts since they have no date).
    Truncated to MAX_ITEMS entries.
    """
    posts     = posts or []
    resources = resources or []

    items: list[str] = []

    # Posts — have publishedAt, sorted by the caller (newest first).
    for post in posts[:MAX_ITEMS]:
        slug = get_slug(post.get("slug"))
        if not slug:
            continue
        link = f"{SITE_URL}/resources/{slug}/"
        items.append(_item(
            title=post.get("title", ""),
            link=link,
            description=post.get("excerpt") or post.get("title", ""),
            pub_date=post.get("publishedAt"),
            author=RSS_AUTHOR,
        ))

    # Resources — append up to remaining slots.
    remaining = MAX_ITEMS - len(items)
    for resource in resources[:remaining]:
        slug = get_slug(resource.get("slug"))
        if not slug:
            continue
        link = f"{SITE_URL}/resources/{slug}/"
        items.append(_item(
            title=resource.get("title", ""),
            link=link,
            description=resource.get("heroDescription") or resource.get("title", ""),
            pub_date=None,
            author=RSS_AUTHOR,
        ))

    now_rfc = format_datetime(datetime.now(timezone.utc))

    xml = "\n".join([
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
        "  <channel>",
        f"    <title>{xml_escape(RSS_TITLE)}</title>",
        f"    <link>{xml_escape(SITE_URL)}</link>",
        f"    <description>{xml_escape(RSS_DESCRIPTION)}</description>",
        f"    <language>en-us</language>",
        f"    <lastBuildDate>{now_rfc}</lastBuildDate>",
        f'    <atom:link href="{xml_escape(SITE_URL)}/rss.xml" rel="self" type="application/rss+xml"/>',
        *items,
        "  </channel>",
        "</rss>",
    ])

    out_path = os.path.join(DIST_DIR, "rss.xml")
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(xml)

    logger.info("  built /rss.xml (%d items)", len(items))
