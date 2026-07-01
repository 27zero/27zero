"""
builders/base.py — SectionBuilder: the reusable CMS section engine.

Every CMS-driven section (Work, Podcasts, Case Studies, …) is a
subclass of SectionBuilder.  The base class owns everything that is
identical across all sections:

  - The build loop  (index page + one detail page per item)
  - Error handling and graceful degradation on template or render failure
  - Item enrichment  (resolved image URLs, category labels)
  - Gallery resolution
  - Related-item scoring
  - Category grouping for filter tabs
  - SEO context construction for index and detail pages
  - Sitemap entry generation
  - Filesystem writes

Subclasses declare section-specific config and override up to five hooks:

  enrich_item(item)       — add resolved image URLs, computed label strings
  body_html(item)         — render portable-text fields → {field: html} dict
  index_context(...)      — full template context dict for the index page
  detail_context(...)     — full template context dict for a detail page
  detail_seo(item, slug)  — SEO context for a detail page

Every hook has a working default.  A minimal subclass only sets class
attributes.

Why one class, not four modules?
---------------------------------
The natural split would be filesystem.py, renderer.py, seo.py,
registry.py.  That split was evaluated and rejected for the following
reason: every method in SectionBuilder reads instance state (section,
category_key, label_map, THUMB_WIDTH, …).  Extracting them into free
functions would require passing that state as parameters, or importing
the class back — replacing one cohesive class with four tightly-coupled
modules.  The Single Responsibility Principle is about reasons to
change, not file count.  SectionBuilder changes when the
section-building algorithm changes: that is one reason.

See ARCHITECTURE.md for the full design rationale.
"""

from __future__ import annotations

import logging
import os
from collections import defaultdict
from typing import Any, Generator

from jinja2 import Environment

from config import DIST_DIR, SITE_URL
from helpers.images import image_url
from helpers.seo import build_seo_context
from helpers.slug import get_slug

logger = logging.getLogger(__name__)


class SectionBuilder:
    """
    Base class for CMS-driven section builders.

    Class attributes — set these in every subclass
    -----------------------------------------------
    section : str
        URL prefix and dist/ subdirectory.
        e.g. ``"work"``  →  /work/  and  dist/work/

    sanity_type : str
        Sanity _type name.  Used only in log messages.
        e.g. ``"workProject"``

    Class attributes — override when the default is wrong
    ------------------------------------------------------
    index_template : str
        Jinja2 template path relative to pages/.
        Default: ``"{section}/index.html"``

    detail_template : str
        Jinja2 template path relative to pages/.
        Default: ``"{section}/detail.html"``

    index_title : str
        <title> tag content for the index page.
        Default: ``"{Section} — 27zero"``

    index_desc : str
        Meta description for the index page.

    index_og_type : str
        Open Graph type for the index page.
        Default: ``"website"``

    category_key : str
        Item field used to group items into filter tabs and to score
        related items.
        Default: ``"category"``

    related_secondary_key : str
        Item field whose values are intersected for secondary related
        scoring.  One point per shared value.
        Default: ``"services"``

    related_limit : int
        Maximum related items on a detail page.
        Default: ``2``

    label_map : dict[str, str]
        Maps category_key values to display labels.
        Unknown values fall back to value.replace("-", " ").title().

    sitemap_changefreq : str
        changefreq for detail-page sitemap entries.
        Default: ``"monthly"``

    sitemap_priority : str
        priority for detail-page sitemap entries.
        Default: ``"0.8"``

    THUMB_WIDTH : int
        Default width for thumbnail CDN URLs.
    HERO_WIDTH : int
        Default width for hero image CDN URLs.
    OG_WIDTH : int
        Width for Open Graph image CDN URLs.
    """

    # ── Required ──────────────────────────────────────────────────────────
    section:     str = ""
    sanity_type: str = ""

    # ── Optional — sensible defaults ──────────────────────────────────────
    index_template:  str = ""
    detail_template: str = ""
    index_title:     str = ""
    index_desc:      str = ""
    index_og_type:   str = "website"
    category_key:           str = "category"
    related_secondary_key:  str = "services"
    related_limit:          int = 2
    label_map:       dict[str, str] = {}
    sitemap_changefreq: str = "monthly"
    sitemap_priority:   str = "0.8"

    # ── Image dimensions ──────────────────────────────────────────────────
    THUMB_WIDTH: int = 800
    HERO_WIDTH:  int = 1600
    OG_WIDTH:    int = 1200

    # =========================================================================
    # Public entry point
    # =========================================================================

    def build(
        self,
        env: Environment,
        items: list[dict[str, Any]],
    ) -> int:
        """
        Build the complete section: index page + one detail page per item.

        Parameters
        ----------
        env:
            Configured Jinja2 Environment shared across all builders.
        items:
            List of document dicts returned by helpers/sanity.py.

        Returns
        -------
        int
            Number of HTML files written (1 index + N details).
        """
        if not items:
            logger.info(
                "No %s documents in Sanity — skipping /%s/ section.",
                self.sanity_type or self.section,
                self.section,
            )
            return 0

        count = 0

        if self._build_index(env, items):
            count += 1

        for item in items:
            if self._build_detail(env, item, items):
                count += 1

        return count

    # =========================================================================
    # Hooks — override in subclasses to add section-specific behaviour
    # =========================================================================

    def enrich_item(self, item: dict[str, Any]) -> dict[str, Any]:
        """
        Return an enriched copy of ``item``.

        The default implementation adds:
          thumbnailUrl  — CDN-optimised thumbnail URL string
          heroUrl       — CDN-optimised hero image URL string
          categoryLabel — human-readable label for the category_key field

        Subclasses that need additional computed fields should call
        ``super().enrich_item(item)`` and extend the returned dict::

            def enrich_item(self, item):
                base = super().enrich_item(item)
                return {
                    **base,
                    "formattedDate": item.get("date", "")[:10],
                }

        Never mutate the original ``item`` dict.  Sanity data is
        treated as immutable throughout the build pipeline.
        """
        return {
            **item,
            "thumbnailUrl":  self._thumb(item),
            "heroUrl":       self._hero(item),
            "categoryLabel": self._label(item.get(self.category_key, "")),
        }

    def body_html(self, item: dict[str, Any]) -> dict[str, str]:
        """
        Render portable-text fields and return a dict of HTML strings.

        The default returns ``{}`` (no rich-text body sections).

        Subclasses that have portable-text fields import
        ``render_portable_text`` directly and render each field::

            from helpers.portable_text import render_portable_text

            def body_html(self, item):
                solution = item.get("solution") or {}
                return {
                    "challenge":     render_portable_text(item.get("challenge") or []),
                    "solution_body": render_portable_text(solution.get("body") or []),
                }

        The keys become template variables accessible as
        ``body_html.challenge``, ``body_html.solution_body``, etc.
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
        Return the complete template context dict for the index page.

        Override when your index template uses different variable names,
        or when you need to add section-specific variables.

        The base implementation provides:
          items              — all enriched items
          categories         — list of {value, label, count} dicts
          items_by_category  — {category_value: [item, ...]}
          featured           — items where featured == True
          seo                — SEO context dict from helpers/seo.py
        """
        return {
            "items":             items,
            "categories":        categories,
            "items_by_category": groups,
            "featured":          featured,
            "seo":               seo,
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
        Return the complete template context dict for a detail page.

        Override when your detail template uses different variable names,
        or when you need to add section-specific variables.

        The base implementation provides:
          item       — the enriched item dict
          body_html  — rendered portable-text fields (from body_html())
          related    — list of enriched related items
          gallery    — list of gallery images with resolved src URLs
          seo        — SEO context dict from helpers/seo.py
        """
        return {
            "item":      item,
            "body_html": body_html,
            "related":   related,
            "gallery":   gallery,
            "seo":       seo,
        }

    def detail_seo(
        self,
        item: dict[str, Any],
        slug: str,
    ) -> dict[str, Any]:
        """
        Build and return the SEO context dict for a detail page.

        Override to customise title format, og_type, or breadcrumbs.
        Delegates to helpers/seo.py — this hook only assembles the
        parameters; it does not duplicate SEO logic.
        """
        section_title = self.section.replace("-", " ").title()
        title = item.get("seoTitle") or item.get("title", slug)
        description = (
            item.get("seoDescription")
            or item.get("excerpt")
            or title
        )
        return build_seo_context(
            url_path=f"{self.section}/{slug}",
            title=f"{title} — 27zero",
            description=description,
            image_url=self._og(item),
            og_type="article",
            breadcrumbs=[
                {"name": "Home",        "url": "/"},
                {"name": section_title, "url": f"/{self.section}/"},
                {"name": item.get("title", slug), "url": f"/{self.section}/{slug}/"},
            ],
        )

    # =========================================================================
    # Sitemap integration
    # =========================================================================

    def sitemap_entries(
        self,
        items: list[dict[str, Any]],
        today: str,
    ) -> Generator[tuple[str, str, str, str], None, None]:
        """
        Yield (loc, lastmod, changefreq, priority) tuples for every URL
        this builder is responsible for.

        Called by builders/sitemap.py.  The sitemap builder does not need
        to know which sections exist — it iterates the registered builders.

        Yields the section index first, then one entry per item.
        Uses ``publishedAt`` as lastmod when present, falling back to today.
        """
        if not items:
            return

        yield (
            f"{SITE_URL}/{self.section}/",
            today,
            "weekly",
            "1.0",
        )

        for item in items:
            slug = item.get("slug") or get_slug(item.get("slug", {}))
            if not slug:
                continue
            lastmod = (item.get("publishedAt") or today)[:10]
            yield (
                f"{SITE_URL}/{self.section}/{slug}/",
                lastmod,
                self.sitemap_changefreq,
                self.sitemap_priority,
            )

    # =========================================================================
    # Image helpers
    # =========================================================================
    # These are private methods rather than free functions so they can read
    # THUMB_WIDTH, HERO_WIDTH, OG_WIDTH from self.  Subclasses may override
    # those class attributes to change default dimensions.

    def _thumb(self, item: dict[str, Any], width: int | None = None) -> str:
        """Return a CDN-optimised thumbnail URL, or '' if no thumbnail."""
        w = width or self.THUMB_WIDTH
        thumb = item.get("thumbnail") or {}
        url = thumb.get("url") if isinstance(thumb, dict) else thumb
        return image_url(url, width=w, auto="format")

    def _hero(self, item: dict[str, Any], width: int | None = None) -> str:
        """Return a CDN-optimised hero image URL, or '' if no hero image."""
        w = width or self.HERO_WIDTH
        hero = item.get("heroImage") or {}
        url = hero.get("url") if isinstance(hero, dict) else hero
        return image_url(url, width=w, auto="format")

    def _og(self, item: dict[str, Any]) -> str:
        """
        Return the OG image URL.

        Fallback chain: ogImage → heroImage → thumbnail → ''
        """
        for field in ("ogImage", "heroImage", "thumbnail"):
            src = item.get(field) or {}
            url = src.get("url") if isinstance(src, dict) else src
            if url:
                return image_url(url, width=self.OG_WIDTH, auto="format")
        return ""

    def _enrich_gallery(self, item: dict[str, Any]) -> list[dict[str, Any]]:
        """Return gallery images with a resolved ``src`` URL added to each."""
        gallery = item.get("gallery") or []
        return [
            {**img, "src": image_url(img.get("url"), width=1200, auto="format")}
            for img in gallery
            if img.get("url")
        ]

    def _label(self, value: str) -> str:
        """Return the display label for a category value."""
        return self.label_map.get(value, value.replace("-", " ").title())

    # =========================================================================
    # Data helpers
    # =========================================================================

    def _group_by(
        self,
        items: list[dict[str, Any]],
    ) -> dict[str, list[dict[str, Any]]]:
        """
        Group items by their ``category_key`` field value.

        Preserves insertion order of first appearance of each key
        (Python 3.7+ dict ordering guarantee).
        """
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for item in items:
            key = item.get(self.category_key) or "other"
            groups[key].append(item)
        return dict(groups)

    def _related(
        self,
        current: dict[str, Any],
        all_items: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Return up to ``related_limit`` items related to ``current``.

        Scoring:
          +2  per item that shares the same category_key value
          +1  per shared value in the related_secondary_key list field

        Items with score 0 are excluded.  Results are sorted by score
        descending, then featured descending, then order ascending.
        The current item is always excluded.
        """
        current_slug = current.get("slug", "")
        current_cat  = current.get(self.category_key, "")
        current_sec  = set(current.get(self.related_secondary_key) or [])

        scored: list[tuple[int, dict[str, Any]]] = []

        for item in all_items:
            if item.get("slug") == current_slug:
                continue
            score = 0
            if item.get(self.category_key) == current_cat:
                score += 2
            shared = set(item.get(self.related_secondary_key) or []) & current_sec
            score += len(shared)
            if score > 0:
                scored.append((score, item))

        scored.sort(
            key=lambda x: (
                -x[0],
                not x[1].get("featured", False),
                x[1].get("order", 100),
            )
        )
        return [item for _, item in scored[: self.related_limit]]

    # =========================================================================
    # Internal build methods
    # =========================================================================

    @property
    def _index_template_name(self) -> str:
        return self.index_template or f"{self.section}/index.html"

    @property
    def _detail_template_name(self) -> str:
        return self.detail_template or f"{self.section}/detail.html"

    def _write(self, html: str, *path_parts: str) -> None:
        """Write ``html`` to dist/{path_parts}/index.html, creating dirs."""
        out_dir = os.path.join(DIST_DIR, *path_parts)
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(html)

    def _build_index(
        self,
        env: Environment,
        items: list[dict[str, Any]],
    ) -> bool:
        """Render and write the section index page.  Returns success flag."""
        try:
            template = env.get_template(self._index_template_name)
        except Exception as exc:
            logger.error(
                "[%s] Could not load index template %r: %s",
                self.section, self._index_template_name, exc,
            )
            return False

        enriched   = [self.enrich_item(item) for item in items]
        groups     = self._group_by(enriched)
        categories = [
            {"value": cat, "label": self._label(cat), "count": len(grp)}
            for cat, grp in groups.items()
        ]
        featured = [item for item in enriched if item.get("featured")]

        seo = build_seo_context(
            url_path=self.section,
            title=self.index_title or f"{self.section.title()} — 27zero",
            description=self.index_desc,
            og_type=self.index_og_type,
            breadcrumbs=[
                {"name": "Home", "url": "/"},
                {"name": self.section.replace("-", " ").title(), "url": f"/{self.section}/"},
            ],
        )

        ctx = self.index_context(
            items=enriched,
            categories=categories,
            groups=groups,
            featured=featured,
            seo=seo,
        )

        try:
            html = template.render(**ctx)
        except Exception as exc:
            logger.error("[%s] Error rendering index: %s", self.section, exc)
            return False

        self._write(html, self.section)
        logger.info(
            "  built /%s/  (%d items, %d categories)",
            self.section, len(enriched), len(categories),
        )
        return True

    def _build_detail(
        self,
        env: Environment,
        item: dict[str, Any],
        all_items: list[dict[str, Any]],
    ) -> bool:
        """Render and write one detail page.  Returns success flag."""
        slug = item.get("slug") or get_slug(item.get("slug", {}))
        if not slug:
            logger.warning(
                "[%s] Skipping item with no slug: %r",
                self.section, item.get("title"),
            )
            return False

        try:
            template = env.get_template(self._detail_template_name)
        except Exception as exc:
            logger.error(
                "[%s] Could not load detail template %r: %s",
                self.section, self._detail_template_name, exc,
            )
            return False

        enriched = self.enrich_item(item)
        related  = [self.enrich_item(rel) for rel in self._related(item, all_items)]

        ctx = self.detail_context(
            item=enriched,
            body_html=self.body_html(item),
            related=related,
            gallery=self._enrich_gallery(item),
            seo=self.detail_seo(item, slug),
        )

        try:
            html = template.render(**ctx)
        except Exception as exc:
            logger.error(
                "[%s] Error rendering detail %r: %s",
                self.section, slug, exc,
            )
            return False

        self._write(html, self.section, slug)
        logger.info("  built /%s/%s/", self.section, slug)
        return True
