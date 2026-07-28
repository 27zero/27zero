"""
builders/practice.py — EdTech Marketing Agency Practice section builder.

Generates:
  /edtech-marketing-agency/           — index page  (built here AND by build_pages;
                                        build_pages runs first and owns this URL —
                                        PracticeBuilder skips index when items exist
                                        so the two never compete)
  /edtech-marketing-agency/{slug}/    — one detail page per practice document

Follows the exact same contract as WorkBuilder:
  1. Section config (class attributes)
  2. enrich_item()    — adds heroImageUrl
  3. body_html()      — no portable-text fields; returns empty dict
  4. index_context()  — exposes `practices` alias
  5. detail_context() — exposes `practice` alias (mirrors WorkBuilder's `project`)

The only departure from WorkBuilder is that build() skips the index page
so it does not overwrite the richer version already produced by build_pages().
"""

from typing import Any

from builders.base import SectionBuilder
from helpers.images import image_url


class PracticeBuilder(SectionBuilder):
    """
    Section builder for EdTech Marketing Agency Practice detail pages.

    Sanity type  : practice
    Section URL  : edtech-marketing-agency/
    Detail URLs  : edtech-marketing-agency/{slug}/
    """

    # ── Section config ─────────────────────────────────────────────────
    section      = "edtech-marketing-agency"
    sanity_type  = "practice"

    index_template  = "edtech-marketing-agency/index.html"
    detail_template = "edtech-marketing-agency/practice/index.html"

    index_title = "EdTech Marketing Agency — 27zero"
    index_desc  = (
        "27zero is the world's only EdTech-exclusive marketing agency. "
        "Marketing programs designed to amplify the impact of EdTech companies."
    )

    category_key          = "title"
    related_secondary_key = "clientNames"
    related_limit         = 2

    # ── Hooks ──────────────────────────────────────────────────────────

    def enrich_item(self, item: dict[str, Any]) -> dict[str, Any]:
        """
        Extend base enrichment with practice-specific fields.

        Adds:
          heroImageUrl — CDN-optimised hero image URL
        """
        base = super().enrich_item(item)
        hero = item.get("heroImage") or {}
        return {
            **base,
            "heroImageUrl": (
                image_url(hero["url"], width=1400, auto="format")
                if hero.get("url") else ""
            ),
        }

    def body_html(self, item: dict[str, Any]) -> dict[str, str]:
        """
        Practice documents have no portable-text body fields.
        Return an empty dict to satisfy the SectionBuilder contract.
        """
        return {}

    def index_context(
        self,
        items: list[dict[str, Any]],
        categories: list[dict[str, Any]],
        groups: dict[str, list[dict[str, Any]]],
        featured: list[dict[str, Any]],
        seo: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Context for the agency index page.
        Exposes `practices` alias so the existing template variable name works.
        """
        return {
            # Generic base names
            "items":             items,
            "categories":        categories,
            "items_by_category": groups,
            "featured":          featured,
            "seo":               seo,
            # Practice-specific alias used by edtech-marketing-agency/index.html
            "practices":         items,
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
        Context for a practice detail page.
        Exposes `practice` alias so the template uses the correct variable name.
        """
        return {
            # Generic base names
            "item":      item,
            "body_html": body_html,
            "related":   related,
            "gallery":   gallery,
            "seo":       seo,
            # Practice-specific alias used by practice/index.html
            "practice":  item,
        }

    def build(
        self,
        env,
        items: list[dict[str, Any]],
    ) -> int:
        """
        Build detail pages only — skip the index page.

        The agency index (/edtech-marketing-agency/) is already built by
        build_pages() with richer context (settings, services menu, etc.).
        PracticeBuilder skips it to avoid overwriting that page.

        Everything else (locale loop, SEO, _write, logging) is handled
        by the inherited _build_detail() — no duplication needed.
        """
        if not items:
            return 0

        from helpers.i18n import LOCALES
        count = 0
        for loc in LOCALES:
            for item in items:
                if self._build_detail(env, item, items, loc):
                    count += 1
        return count
