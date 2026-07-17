"""
helpers/seo.py — SEO metadata builder.

Produces a dict of SEO context variables that templates consume via
Jinja2 blocks.  Every page that calls build_seo_context() gets full
canonical, Open Graph, Twitter Card, and JSON-LD coverage
automatically.

Usage in builders
-----------------
    from helpers.seo import build_seo_context

    seo = build_seo_context(
        url_path="resources/my-article",
        title="My Article",
        description="Short description.",
        image_url="https://cdn.sanity.io/...",
        type="article",
        published_at="2026-01-15T09:00:00Z",
        author_name="27zero",
    )
    html = template.render(**context, seo=seo)

Template usage (base.html)
--------------------------
    {% if seo.canonical %}
    <link rel="canonical" href="{{ seo.canonical }}">
    {% endif %}
    {{ seo.meta_tags|safe }}
    {{ seo.json_ld|safe }}
"""

import json
from datetime import datetime, timezone
from html import escape
from typing import Any

from config import SITE_URL, SITE_NAME, SITE_DESCRIPTION
from helpers.i18n import hreflang_links as _hreflang_links


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _canonical(url_path: str) -> str:
    """Return an absolute canonical URL for ``url_path``."""
    path = url_path.strip("/")
    if path:
        return f"{SITE_URL}/{path}/"
    return f"{SITE_URL}/"


def _fmt_date(iso: str | None) -> str:
    """Parse an ISO 8601 string and return YYYY-MM-DD, or today if None."""
    if iso:
        try:
            return iso[:10]
        except Exception:
            pass
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_seo_context(
    url_path: str,
    title: str | None = None,
    description: str | None = None,
    image_url: str | None = None,
    og_type: str = "website",
    published_at: str | None = None,
    modified_at: str | None = None,
    author_name: str | None = None,
    breadcrumbs: list[dict[str, str]] | None = None,
    url_path_neutral: str | None = None,
    locale: str = "en",
    og_locale: str = "en_US",
) -> dict[str, Any]:
    """
    Build a complete SEO context dict for a single page.

    Parameters
    ----------
    url_path:
        Site-relative URL path, e.g. ``"resources/my-article"``.
        The canonical URL is derived from this.
    title:
        Page title.  Falls back to SITE_NAME.
    description:
        Meta description.  Falls back to SITE_DESCRIPTION.
    image_url:
        Absolute URL for OG image.
        Falls back to a default OG image if configured.
    og_type:
        Open Graph type.  ``"website"`` or ``"article"``.
    published_at:
        ISO 8601 publish date (articles only).
    modified_at:
        ISO 8601 modification date (articles only).
    author_name:
        Human-readable author name for structured data.
    breadcrumbs:
        List of ``{"name": "…", "url": "…"}`` dicts for BreadcrumbList.

    Returns
    -------
    dict with keys:
        canonical   — absolute canonical URL string
        title       — resolved page title
        description — resolved meta description
        meta_tags   — safe HTML string of all <meta> tags
        json_ld     — safe HTML <script type="application/ld+json"> block
    """
    resolved_title = title or SITE_NAME
    resolved_desc  = description or SITE_DESCRIPTION
    canonical      = _canonical(url_path)
    resolved_image = image_url or ""

    # ── Open Graph / Twitter meta tags ──────────────────────────────────
    tags: list[str] = [
        f'<meta property="og:site_name" content="{escape(SITE_NAME)}">',
        f'<meta property="og:title" content="{escape(resolved_title)}">',
        f'<meta property="og:description" content="{escape(resolved_desc)}">',
        f'<meta property="og:type" content="{escape(og_type)}">',
        f'<meta property="og:url" content="{escape(canonical)}">',
        f'<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{escape(resolved_title)}">',
        f'<meta name="twitter:description" content="{escape(resolved_desc)}">',
    ]

    # og:locale for the current page; og:locale:alternate for the other locales
    tags.append(f'<meta property="og:locale" content="{escape(og_locale)}">')
    # Import here to avoid circular import at module level
    from helpers.i18n import LOCALES as _LOCALES
    _og_locale_map = {"en-us": "en_US", "en-eu": "en_GB", "es-419": "es_419"}
    for _loc in _LOCALES:
        _alt_og = _og_locale_map.get(_loc["key"], "en_US")
        if _alt_og != og_locale:
            tags.append(f'<meta property="og:locale:alternate" content="{escape(_alt_og)}">')

    if resolved_image:
        tags += [
            f'<meta property="og:image" content="{escape(resolved_image)}">',
            f'<meta name="twitter:image" content="{escape(resolved_image)}">',
        ]

    if og_type == "article" and published_at:
        tags.append(
            f'<meta property="article:published_time" '
            f'content="{escape(published_at)}">'
        )
    if og_type == "article" and modified_at:
        tags.append(
            f'<meta property="article:modified_time" '
            f'content="{escape(modified_at)}">'
        )

    meta_tags = "\n".join(tags)

    # ── JSON-LD structured data ──────────────────────────────────────────
    ld_graphs: list[dict[str, Any]] = []

    # Organization schema — included on every page.
    ld_graphs.append({
        "@type": "Organization",
        "@id": f"{SITE_URL}/#organization",
        "name": SITE_NAME,
        "url": SITE_URL,
        "sameAs": ["https://www.linkedin.com/company/27zero/"],
    })

    # WebSite schema — included on every page.
    ld_graphs.append({
        "@type": "WebSite",
        "@id": f"{SITE_URL}/#website",
        "url": SITE_URL,
        "name": SITE_NAME,
        "description": SITE_DESCRIPTION,
        "publisher": {"@id": f"{SITE_URL}/#organization"},
    })

    # WebPage schema — every page.
    webpage: dict[str, Any] = {
        "@type": "WebPage",
        "@id": canonical,
        "url": canonical,
        "name": resolved_title,
        "description": resolved_desc,
        "inLanguage": locale,
        "isPartOf": {"@id": f"{SITE_URL}/#website"},
    }
    if resolved_image:
        webpage["image"] = resolved_image
    ld_graphs.append(webpage)

    # Article schema — only for content pages.
    if og_type == "article":
        article: dict[str, Any] = {
            "@type": "Article",
            "headline": resolved_title,
            "description": resolved_desc,
            "url": canonical,
            "isPartOf": {"@id": canonical},
            "publisher": {"@id": f"{SITE_URL}/#organization"},
            "datePublished": _fmt_date(published_at),
            "dateModified": _fmt_date(modified_at or published_at),
        }
        if resolved_image:
            article["image"] = resolved_image
        if author_name:
            article["author"] = {"@type": "Person", "name": author_name}
        ld_graphs.append(article)

    # BreadcrumbList schema.
    if breadcrumbs:
        bc_items = [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": crumb["name"],
                "item": crumb["url"] if crumb["url"].startswith("http")
                         else f"{SITE_URL}/{crumb['url'].lstrip('/')}",
            }
            for i, crumb in enumerate(breadcrumbs)
        ]
        ld_graphs.append({
            "@type": "BreadcrumbList",
            "itemListElement": bc_items,
        })

    ld_json = json.dumps(
        {"@context": "https://schema.org", "@graph": ld_graphs},
        ensure_ascii=False,
        separators=(",", ":"),
    )
    json_ld = f'<script type="application/ld+json">{ld_json}</script>'

    # ── Hreflang alternate links ────────────────────────────────────────
    # url_path_neutral is the path without any locale prefix.
    # If not supplied, fall back to url_path.
    neutral = url_path_neutral if url_path_neutral is not None else url_path
    hreflang = _hreflang_links(neutral, SITE_URL)

    return {
        "canonical":     canonical,
        "title":         resolved_title,
        "description":   resolved_desc,
        "image":         resolved_image,
        "meta_tags":     meta_tags,
        "json_ld":       json_ld,
        "hreflang_links": hreflang,
    }
