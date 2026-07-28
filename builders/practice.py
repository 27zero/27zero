"""
builders/practice.py — EdTech Marketing Agency Practice detail builder.

Generates:
  /edtech-marketing-agency/{slug}/   — one detail page per practice document

The agency INDEX (/edtech-marketing-agency/) is already built by
build_pages() because it combines practices with the services menu and
settings-driven content.  PracticeBuilder deliberately skips the index
to avoid overwriting that page.

This builder follows the same pattern as WorkBuilder — it extends
SectionBuilder and only overrides what is practice-specific:

  1. section / sanity_type / template names
  2. enrich_item()  — resolves heroImageUrl
  3. detail_context() — exposes `practice` alias (like WorkBuilder's `project`)
  4. build()        — skips index, builds detail pages only
"""

from typing import Any

from builders.base import SectionBuilder
from helpers.images import image_url


class PracticeBuilder(SectionBuilder):
    """
    Detail-only builder for EdTech Marketing Agency Practice pages.

    Sanity type  : practice
    Detail URL   : /edtech-marketing-agency/{slug}/
    Index URL    : skipped — built by build_pages()
    """

    section      = "edtech-marketing-agency"
    sanity_type  = "practice"

    # Templates
    index_template  = "edtech-marketing-agency/index.html"   # unused — see build()
    detail_template = "edtech-marketing-agency/practice/index.html"

    # SEO defaults for detail pages
    index_title = "EdTech Marketing Agency — 27zero"
    index_desc  = (
        "27zero is the world's only EdTech-exclusive marketing agency."
    )
    category_key = "title"

    # ── Hooks ─────────────────────────────────────────────────────────────

    def enrich_item(self, item: dict[str, Any]) -> dict[str, Any]:
        """Add heroImageUrl to base enrichment."""
        base = super().enrich_item(item)
        hero = item.get("heroImage") or {}
        return {
            **base,
            "heroImageUrl": (
                image_url(hero["url"], width=1400, auto="format")
                if hero.get("url") else ""
            ),
        }

    def detail_context(
        self,
        item: dict[str, Any],
        body_html: dict[str, str],
        related: list[dict[str, Any]],
        gallery: list[dict[str, Any]],
        seo: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Expose `practice` as the main template variable.
        Also keeps the generic `item` name for consistency.
        """
        return {
            "item":      item,
            "body_html": body_html,
            "related":   related,
            "gallery":   gallery,
            "seo":       seo,
            # Practice-specific alias used by the template
            "practice":  item,
        }

    def build(self, env, items):
        """
        Build detail pages only — skip index (already built by build_pages).
        Reuses base._build_detail() unchanged — no custom loop needed.
        """
        if not items:
            return 0

        from helpers.i18n import LOCALES as _LOCALES
        count = 0
        for loc in _LOCALES:
            for item in items:
                if self._build_detail(env, item, items, loc):
                    count += 1
        return count
