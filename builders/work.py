"""
builders/work.py — Work / Case Study section builder.

Generates:
  /work/              — index: all projects, category filter tabs
  /work/{slug}/       — detail: brief, challenge, solution, impact, gallery

This file is intentionally short.  All render loops, filesystem writes,
SEO wiring, and related-item logic live in builders/base.py.
WorkBuilder overrides only what is specific to Work:

  1. Section config (class attributes)
  2. enrich_item()      — thumbnailUrl, heroUrl, categoryLabel (inherited
                          default is sufficient here; kept for explicitness)
  3. body_html()        — renders challenge and solution portable-text fields
  4. index_context()    — exposes `projects` / `projects_by_category` aliases
                          so existing templates don't need renaming
  5. detail_context()   — exposes `project` alias for the detail template

Context aliases
---------------
The base class uses generic variable names (item, items, items_by_category).
Work templates were written with section-specific names (project, projects,
projects_by_category).  Rather than rename all templates, we override the
two context methods to add both sets of names.  Future sections should
use the generic names from the start.
"""

from typing import Any

from builders.base import SectionBuilder
from helpers.portable_text import render_portable_text


class WorkBuilder(SectionBuilder):
    """
    Section builder for Work / Case Study pages.

    Sanity type : workProject
    URL prefix  : /work/
    """

    # ── Section config ────────────────────────────────────────────────
    section      = "work"
    sanity_type  = "workProject"

    index_title  = "Work — Behind the fastest-growing EdTech brands — 27zero"
    index_desc   = (
        "First-hand expertise, innovative conceptual thinking & design, "
        "client-first approach. Explore our EdTech case studies."
    )

    category_key          = "category"
    related_secondary_key = "services"
    related_limit         = 2

    label_map = {
        "brand-essentials":    "Brand Essentials",
        "marketing-programs":  "Marketing Programs",
        "customer-spotlights": "Customer Spotlights",
        "events-experiences":  "Events & Experiences",
        "video-motion":        "Video & Motion",
        "gtm-launch":          "GTM & Launch",
    }

    # ── Hooks ─────────────────────────────────────────────────────────

    def body_html(self, item: dict[str, Any]) -> dict[str, str]:
        """Render the two portable-text fields used on the Work detail page."""
        solution = item.get("solution") or {}
        return {
            "challenge":     render_portable_text(item.get("challenge") or []),
            "solution_body": render_portable_text(solution.get("body") or []),
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
        Extend the base context with Work template variable names.

        The Work index template uses ``projects``, ``projects_by_category``,
        and ``featured`` rather than the generic base-class names.
        Both names are provided so either can be used.
        """
        return {
            # Generic base names
            "items":              items,
            "categories":         categories,
            "items_by_category":  groups,
            "featured":           featured,
            "seo":                seo,
            # Work-specific aliases (used by existing templates)
            "projects":               items,
            "projects_by_category":   groups,
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
        Extend the base context with Work template variable names.

        The Work detail template uses ``project`` rather than the generic
        ``item``.  Both are provided.
        """
        return {
            # Generic base names
            "item":      item,
            "body_html": body_html,
            "related":   related,
            "gallery":   gallery,
            "seo":       seo,
            # Work-specific alias
            "project":   item,
        }


# ---------------------------------------------------------------------------
# Module-level convenience function
# ---------------------------------------------------------------------------

def build_work(env, projects: list[dict[str, Any]]) -> int:
    """Build the complete Work section.  Returns pages written."""
    return WorkBuilder().build(env, projects)
