"""
builders/mentor.py — EdTech Mentor section builder.

Generates:
  /edtech-mentor-interviews/         — index: featured card + three series sliders
  /edtech-mentor-interviews/{slug}/  — detail: full interview page

Follows exactly the same architecture as builders/work.py.
All render loops, filesystem writes, SEO wiring, and related-item logic
live in builders/base.py.  MentorBuilder overrides only what is specific
to this section:

  1. Section config (class attributes)
  2. enrich_item()    — resolves guestPhoto URL and computes initials for avatar
  3. body_html()      — renders the interview body portable-text field
  4. index_context()  — exposes mentor-specific template variable names:
                        featured_interview, series_groups, series_labels
  5. detail_context() — exposes ``interview`` alias for the detail template
  6. detail_seo()     — uses guestName as the page title fallback

Series grouping
---------------
Interviews are grouped by their ``series`` field into three sliders:
  "essencial" → Essential Series
  "investor"  → Investor Series
  "founders"  → Founders Series

The featured card is the first interview with ``featured == True``.
If no interview is marked featured, the most recent one is used.

Sanity fields required
----------------------
The ``interview`` schema must have:
  series    string  "essencial" | "investor" | "founders"
  featured  boolean true for the interview shown in the featured card
  title     string  episode headline shown on cards and the detail page

These fields extend the existing schema.  Existing documents without
these fields will render with graceful fallbacks.
"""

from typing import Any

from builders.base import SectionBuilder
from helpers.images import image_url
from helpers.portable_text import render_portable_text


# Series display config — single source of truth.
# Matches the data-filter values in the existing HTML.
SERIES_CONFIG: list[dict] = [
    {
        "key":         "essencial",
        "label":       "Essential Series",
        "subtitle":    "Pearls of wisdom from seasoned EdTech Leaders.",
        "section_css": "section--essential-mentor",
        "container":   "essential-mentor-container",
        "actions_css": "essential-mentor-actions",
    },
    {
        "key":         "investor",
        "label":       "Investor Series",
        "subtitle":    "The Impact of Investment in EdTech, hosted by Phill Miller",
        "section_css": "section--investor-mentor",
        "container":   "investor-mentor-container",
        "actions_css": "investor-mentor-actions",
    },
    {
        "key":         "founders",
        "label":       "Founders Series",
        "subtitle":    "Conversations with EdTech founders about growth and impact.",
        "section_css": "section--founders-mentor",
        "container":   "founders-mentor-container",
        "actions_css": "founders-mentor-actions",
    },
]


class MentorBuilder(SectionBuilder):
    """
    Section builder for The EdTech Mentor interview pages.

    Sanity type : interview
    URL prefix  : /edtech-mentor-interviews/
    """

    # ── Section config ────────────────────────────────────────────────
    section      = "edtech-mentor-interviews"
    sanity_type  = "interview"

    # Template files live in pages/edtech-mentor/ (the existing folder).
    # The URL prefix is edtech-mentor-interviews/ (matching existing site URLs).
    # We set these explicitly so the base class uses the right paths.
    index_template  = "edtech-mentor/index.html"
    detail_template = "edtech-mentor/detail.html"

    index_title  = "The EdTech Mentor Interview Series — 27zero"
    index_desc   = (
        "Global EdTech leaders sharing their perspectives, experiences, "
        "and valuable lessons from their journey in this formidable industry."
    )

    # Interviews are grouped by series; no secondary scoring key needed.
    category_key          = "series"
    related_secondary_key = "guestCompany"
    related_limit         = 3

    label_map = {s["key"]: s["label"] for s in SERIES_CONFIG}

    # ── Image dimensions ──────────────────────────────────────────────
    THUMB_WIDTH = 200   # guest photo is a small avatar
    OG_WIDTH    = 1200

    # ── Hooks ─────────────────────────────────────────────────────────

    def enrich_item(self, item: dict[str, Any]) -> dict[str, Any]:
        """
        Extend base enrichment with mentor-specific computed fields.

        Adds:
          guestPhotoUrl — CDN-optimised guest photo URL
          initials      — two-letter initials for the avatar fallback
          cardTitle     — title shown on index cards (title or guestName)
          seriesLabel   — human-readable series name
        """
        # Resolve guest photo through image_url so CDN params are applied.
        photo_url = image_url(
            item.get("guestPhoto"), width=self.THUMB_WIDTH, auto="format"
        )

        # Initials: first letter of first name + first letter of last name.
        name = item.get("guestName") or ""
        parts = name.strip().split()
        initials = (
            (parts[0][0] + parts[-1][0]).upper()
            if len(parts) >= 2
            else (parts[0][:2].upper() if parts else "?")
        )

        return {
            **item,
            "guestPhotoUrl": photo_url,
            "initials":      initials,
            "cardTitle":     item.get("title") or item.get("guestName") or "",
            "seriesLabel":   self._label(item.get("series") or ""),
        }

    def body_html(self, item: dict[str, Any]) -> dict[str, str]:
        """Render the interview body portable-text field."""
        return {
            "body": render_portable_text(item.get("body") or []),
        }

    def index_context(
        self,
        items: list[dict[str, Any]],
        categories: list[dict[str, Any]],
        groups: dict[str, list[dict[str, Any]]],
        featured: list[dict[str, Any]],
        seo: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Build the template context for the EdTech Mentor index.

        Exposes:
          interviews        — all enriched interview dicts
          featured_interview — single interview dict for the featured card
          series            — SERIES_CONFIG list with display metadata
          series_groups     — {series_key: [interview, ...]}
          seo               — SEO context from helpers/seo.py
        """
        # Featured interview: first explicitly marked, else first in list.
        feat = featured[0] if featured else (items[0] if items else None)

        return {
            # Generic base names (kept for consistency)
            "items":             items,
            "categories":        categories,
            "items_by_category": groups,
            "featured":          featured,
            "seo":               seo,
            # Mentor-specific names used by the template
            "interviews":          items,
            "featured_interview":  feat,
            "series":              SERIES_CONFIG,
            "series_groups":       groups,
        }

    def detail_context(
        self,
        item: dict[str, Any],
        body_html: dict[str, str],
        related: list[dict[str, Any]],
        gallery: list[dict[str, Any]],
        seo: dict[str, Any],
    ) -> dict[str, Any]:
        """Expose ``interview`` alias for the detail template."""
        return {
            "item":        item,
            "body_html":   body_html,
            "related":     related,
            "gallery":     gallery,
            "seo":         seo,
            # Mentor-specific alias
            "interview":   item,
        }

    def detail_seo(self, item: dict[str, Any], slug: str, loc: dict[str, str]) -> dict[str, Any]:
        """
        Build SEO context for a detail page.

        Uses guestName as the title when seoTitle is absent, since
        interview documents may not have a generic ``title`` field.

        ``loc`` is the current locale entry; it drives the locale-prefixed
        canonical URL and hreflang set, matching the base-class behaviour.
        """
        from helpers.seo import build_seo_context
        from helpers.i18n import prefix_url
        from builders.base import OG_LOCALE_MAP

        guest   = item.get("guestName") or slug
        episode = item.get("title") or guest
        title   = item.get("seoTitle") or f"{episode} — The EdTech Mentor — 27zero"
        desc    = (
            item.get("seoDescription")
            or item.get("excerpt")
            or f"{guest}, {item.get('guestRole') or ''}, {item.get('guestCompany') or ''}"
        ).strip(", ")

        og = (item.get("ogImage") or {}).get("url") or item.get("guestPhoto") or ""

        neutral   = f"{self.section}/{slug}"
        localized = prefix_url(neutral, loc["prefix"])

        return build_seo_context(
            url_path=localized,
            url_path_neutral=neutral,
            title=title,
            description=desc,
            image_url=image_url(og, width=self.OG_WIDTH, auto="format") if og else "",
            og_type="article",
            locale="es" if loc["key"].startswith("es") else "en",
            og_locale=OG_LOCALE_MAP.get(loc["key"], "en_US"),
            breadcrumbs=[
                {"name": "Home",             "url": "/"},
                {"name": "The EdTech Mentor","url": f"/{self.section}/"},
                {"name": guest,               "url": f"/{self.section}/{slug}/"},
            ],
        )


# ---------------------------------------------------------------------------
# Module-level convenience function
# ---------------------------------------------------------------------------

def build_mentor(env, interviews: list[dict[str, Any]]) -> int:
    """Build the complete EdTech Mentor section.  Returns pages written."""
    return MentorBuilder().build(env, interviews)
