"""
helpers/slug.py — Slug and URL utilities.

Small helpers for working with Sanity slug objects and building
site-relative URL paths.
"""

import re
import unicodedata


def get_slug(slug_field: dict | str | None) -> str:
    """
    Extract the slug string from a Sanity slug field.

    Sanity slug fields are objects: ``{"_type": "slug", "current": "my-slug"}``.
    This helper handles both the object form and a plain string.

    Returns an empty string if the input is None or malformed.
    """
    if not slug_field:
        return ""
    if isinstance(slug_field, str):
        return slug_field
    if isinstance(slug_field, dict):
        return slug_field.get("current", "")
    return ""


def slugify(text: str) -> str:
    """
    Convert arbitrary text to a URL-safe slug.

    Used when auto-generating slugs from titles, not when consuming
    Sanity slugs (which are already canonical).

    Example::

        slugify("How EdTech Companies Generate Pipeline")
        # → "how-edtech-companies-generate-pipeline"
    """
    # Normalise unicode (NFD decomposes accented characters).
    text = unicodedata.normalize("NFD", text)
    # Drop combining characters (the accent diacritics).
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = text.lower()
    # Replace anything that isn't alphanumeric or a hyphen with a hyphen.
    text = re.sub(r"[^a-z0-9]+", "-", text)
    # Strip leading/trailing hyphens.
    return text.strip("-")


def resource_url(slug: str) -> str:
    """Return the site-relative URL for a resource page."""
    return f"/resources/{slug}/"


def post_url(slug: str) -> str:
    """Return the site-relative URL for a blog post page."""
    return f"/resources/{slug}/"


def interview_url(slug: str) -> str:
    """Return the site-relative URL for an interview page."""
    return f"/edtech-mentor-interviews/{slug}/"
