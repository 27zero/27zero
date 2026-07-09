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
from helpers.images import image_url
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

    # The index template is the CMS-driven work listing.
    # The detail template is the designer's work-cms article page.
    index_template  = "work/index.html"
    detail_template = "work/work-cms/index.html"

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

    def enrich_item(self, item: dict[str, Any]) -> dict[str, Any]:
        """
        Extend base enrichment with fields needed by the work-cms template.

        Adds:
          clientLogoUrl      — CDN URL for the client logo image
          authorPhotoUrl     — CDN URL for the testimonial author photo
          contentSectionImgs — list of lists of resolved image URLs per section
        """
        base = super().enrich_item(item)

        # Client logo
        logo = item.get("clientLogo") or {}
        client_logo_url = image_url(logo.get("url", ""), width=200, auto="format") if logo.get("url") else ""

        # Testimonial author photo
        testimonial = item.get("testimonial") or {}
        author_photo = testimonial.get("authorPhoto") or {}
        author_photo_url = image_url(author_photo.get("url", ""), width=80, auto="format") if author_photo.get("url") else ""

        # Content section images — resolve each section's image list
        content_sections = item.get("contentSections") or []
        enriched_sections = []
        for section in content_sections:
            images = section.get("images") or []
            enriched_images = [
                {**img, "src": image_url(img.get("url", ""), width=800, auto="format")}
                for img in images if img.get("url")
            ]
            enriched_sections.append({**section, "images": enriched_images})

        return {
            **base,
            "clientLogoUrl":     client_logo_url,
            "authorPhotoUrl":    author_photo_url,
            "contentSections":   enriched_sections,
        }

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

        The work-cms/index.html template uses ``project`` as its main
        variable.  All enriched fields (clientLogoUrl, authorPhotoUrl,
        contentSections) are already on the enriched item dict.
        """
        return {
            # Generic base names
            "item":      item,
            "body_html": body_html,
            "related":   related,
            "gallery":   gallery,
            "seo":       seo,
            # Work-specific alias used by work-cms/index.html
            "project":   item,
        }


# ---------------------------------------------------------------------------
# Module-level convenience function
# ---------------------------------------------------------------------------

def build_work(env, projects: list[dict[str, Any]]) -> int:
    """Build the complete Work section.  Returns pages written."""
    return WorkBuilder().build(env, projects)
