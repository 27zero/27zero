"""
builders/posts.py — Dynamic CMS content builder.

Generates one HTML page per document fetched from Sanity.
Currently handles: posts (blog), resources, and interviews.

Each content type uses its own Jinja2 template and URL namespace.
When the unified content model is adopted, this module can be
simplified to a single loop that routes on ``contentType``.
"""

import logging
import os
from typing import Any

from jinja2 import Environment

from config import DIST_DIR
from helpers.portable_text import render_portable_text
from helpers.seo import build_seo_context
from helpers.slug import get_slug
from helpers.images import image_url

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Posts (blog)
# ---------------------------------------------------------------------------

def build_posts(
    env: Environment,
    posts: list[dict[str, Any]],
) -> int:
    """
    Generate one page per post document.

    URL pattern: /resources/{slug}/
    Template:    pages/resources/post.html

    Posts currently live under /resources/ to match existing URL structure.
    """
    if not posts:
        logger.info("No posts to build.")
        return 0

    try:
        template = env.get_template("resources/post.html")
    except Exception as exc:
        logger.error("Could not load post template: %s", exc)
        return 0

    count = 0
    for post in posts:
        slug = get_slug(post.get("slug"))
        if not slug:
            logger.warning("Skipping post with no slug: %r", post.get("title"))
            continue

        body_html = render_portable_text(post.get("body", []))

        # Resolve featured image URL with sensible defaults.
        feat_image = post.get("featuredImage") or {}
        feat_image_url = image_url(feat_image.get("url"), width=1200, auto="format")

        url_path = f"resources/{slug}"
        seo = build_seo_context(
            url_path=url_path,
            title=post.get("seoTitle") or post.get("title"),
            description=post.get("seoDescription") or post.get("excerpt"),
            image_url=feat_image_url,
            og_type="article",
            published_at=post.get("publishedAt"),
            author_name=(post.get("author") or {}).get("name"),
            breadcrumbs=[
                {"name": "Home",      "url": "/"},
                {"name": "Resources", "url": "/resources/"},
                {"name": post.get("title", slug), "url": f"/{url_path}/"},
            ],
        )

        try:
            html = template.render(post=post, body_html=body_html, seo=seo)
        except Exception as exc:
            logger.error("Error rendering post %r: %s", slug, exc)
            continue

        out_dir = os.path.join(DIST_DIR, "resources", slug)
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(html)

        logger.info("  built /resources/%s/", slug)
        count += 1

    return count


# ---------------------------------------------------------------------------
# Resources (CMS-driven)
# ---------------------------------------------------------------------------

def build_resources(
    env: Environment,
    resources: list[dict[str, Any]],
) -> int:
    """
    Generate one page per resource document.

    URL pattern: /resources/{slug}/
    Template:    pages/resources/post.html  (reused — same layout)

    Resources and posts share the same URL namespace (/resources/).
    Slugs must be unique across both types; Sanity enforces this
    within a single type, so be careful when migrating to a
    unified model.
    """
    if not resources:
        logger.info("No CMS resources to build.")
        return 0

    try:
        template = env.get_template("resources/post.html")
    except Exception as exc:
        logger.error("Could not load resource template: %s", exc)
        return 0

    count = 0
    for resource in resources:
        slug = get_slug(resource.get("slug"))
        if not slug:
            logger.warning("Skipping resource with no slug: %r", resource.get("title"))
            continue

        body_html = render_portable_text(resource.get("body", []))

        # Adapt the resource shape to match the post template's expectations.
        post_ctx = {
            "title":          resource.get("title", ""),
            "excerpt":        resource.get("heroDescription", ""),
            "publishedAt":    None,
            "seoTitle":       resource.get("seoTitle") or resource.get("title"),
            "seoDescription": resource.get("seoDescription") or resource.get("heroDescription"),
            "featuredImage":  None,
            "author":         None,
            "categories":     [],
        }

        url_path = f"resources/{slug}"
        seo = build_seo_context(
            url_path=url_path,
            title=post_ctx["seoTitle"],
            description=post_ctx["seoDescription"],
            og_type="article",
            breadcrumbs=[
                {"name": "Home",      "url": "/"},
                {"name": "Resources", "url": "/resources/"},
                {"name": resource.get("title", slug), "url": f"/{url_path}/"},
            ],
        )

        try:
            html = template.render(post=post_ctx, body_html=body_html, seo=seo)
        except Exception as exc:
            logger.error("Error rendering resource %r: %s", slug, exc)
            continue

        out_dir = os.path.join(DIST_DIR, "resources", slug)
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(html)

        logger.info("  built /resources/%s/ (resource)", slug)
        count += 1

    return count


# ---------------------------------------------------------------------------
# Interviews (EdTech Mentor)
# ---------------------------------------------------------------------------

def build_interviews(
    env: Environment,
    interviews: list[dict[str, Any]],
) -> int:
    """
    Generate one page per interview document.

    URL pattern: /edtech-mentor-interviews/{slug}/
    Template:    pages/edtech-mentor/interview.html

    Falls back to a stub page if the interview template doesn't exist yet.
    """
    if not interviews:
        logger.info("No interviews to build.")
        return 0

    # Try the dedicated interview template first; fall back to post layout.
    template_name = "edtech-mentor/interview.html"
    try:
        template = env.get_template(template_name)
    except Exception:
        logger.warning(
            "Interview template %r not found; falling back to post layout.",
            template_name,
        )
        try:
            template = env.get_template("resources/post.html")
        except Exception as exc:
            logger.error("No fallback template available: %s", exc)
            return 0

    count = 0
    for interview in interviews:
        slug = get_slug(interview.get("slug"))
        if not slug:
            logger.warning(
                "Skipping interview with no slug: %r", interview.get("guestName")
            )
            continue

        body_html = render_portable_text(interview.get("body", []))

        # Map interview fields to what the post template expects.
        guest_name = interview.get("guestName", "")
        title = f"{guest_name} — The EdTech Mentor"
        post_ctx = {
            "title":          title,
            "excerpt":        f"{interview.get('guestRole', '')} at {interview.get('guestCompany', '')}",
            "publishedAt":    None,
            "seoTitle":       interview.get("seoTitle") or title,
            "seoDescription": interview.get("seoDescription") or post_ctx_desc(interview),
            "featuredImage":  {"url": interview.get("guestPhoto")},
            "author":         None,
            "categories":     [],
        }

        url_path = f"edtech-mentor-interviews/{slug}"
        seo = build_seo_context(
            url_path=url_path,
            title=post_ctx["seoTitle"],
            description=post_ctx["seoDescription"],
            image_url=interview.get("guestPhoto"),
            og_type="article",
            breadcrumbs=[
                {"name": "Home",             "url": "/"},
                {"name": "The EdTech Mentor","url": "/edtech-mentor-interviews/"},
                {"name": guest_name,          "url": f"/{url_path}/"},
            ],
        )

        try:
            html = template.render(
                interview=interview,
                post=post_ctx,
                body_html=body_html,
                seo=seo,
            )
        except Exception as exc:
            logger.error("Error rendering interview %r: %s", slug, exc)
            continue

        out_dir = os.path.join(DIST_DIR, "edtech-mentor-interviews", slug)
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(html)

        logger.info("  built /edtech-mentor-interviews/%s/", slug)
        count += 1

    return count


def post_ctx_desc(interview: dict) -> str:
    """Build a fallback description from interview fields."""
    parts = [interview.get("guestName", "")]
    role = interview.get("guestRole")
    company = interview.get("guestCompany")
    if role:
        parts.append(role)
    if company:
        parts.append(company)
    return " — ".join(p for p in parts if p)
