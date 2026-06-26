"""
helpers/sanity.py — Sanity Content Lake client.

All interaction with the Sanity API is centralised here.
build.py and builders/ import from this module; they never
call requests.get directly.

Architecture note
-----------------
The project currently has three document types: post, resource,
interview.  They are fetched with separate functions so the build
can handle them individually.  The long-term goal is one unified
``post`` document with a ``contentType`` discriminator field;  when
that migration happens only this file needs updating.
"""

import logging
from typing import Any

import requests

from config import SANITY_API_URL, SANITY_TOKEN, VERBOSE

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Internal transport
# ---------------------------------------------------------------------------

def _query(groq: str) -> list[dict[str, Any]]:
    """
    Execute a GROQ query against the Sanity Content Query API.

    Returns the ``result`` array from the response.
    Raises ``requests.HTTPError`` on non-2xx responses.
    Raises ``requests.ConnectionError`` / ``requests.Timeout`` on network issues.
    The caller (builders/) is responsible for catching these and deciding
    whether to abort the build or continue with stale data.
    """
    headers: dict[str, str] = {}
    if SANITY_TOKEN:
        headers["Authorization"] = f"Bearer {SANITY_TOKEN}"

    if VERBOSE:
        logger.debug("Sanity GROQ: %s", groq.strip())

    response = requests.get(
        SANITY_API_URL,
        params={"query": groq},
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()

    result = response.json().get("result", [])

    if VERBOSE:
        logger.debug("Sanity returned %d documents", len(result))

    return result


# ---------------------------------------------------------------------------
# Post (blog) queries
# ---------------------------------------------------------------------------

# GROQ projection shared between list and detail queries.
# Adding a field here makes it available everywhere posts are used.
_POST_PROJECTION = """
    _id,
    title,
    slug,
    excerpt,
    publishedAt,
    body,
    seoTitle,
    seoDescription,
    "featuredImage": {
        "url": mainImage.asset->url,
        "alt": mainImage.alt,
        "lqip": mainImage.asset->metadata.lqip
    },
    "author": {
        "name": author->name,
        "role": author->role,
        "slug": author->slug.current,
        "photo": author->photo.asset->url
    },
    "categories": categories[]->{ title, "slug": slug.current }
"""


def get_posts() -> list[dict[str, Any]]:
    """
    Fetch all published posts ordered newest-first.
    Corresponds to documents with _type == "post".
    """
    groq = f"""
    *[_type == "post" && defined(slug.current)]
    | order(publishedAt desc)
    {{
        {_POST_PROJECTION}
    }}
    """
    return _query(groq)


def get_featured_posts(limit: int = 3) -> list[dict[str, Any]]:
    """Return the most recent ``limit`` posts (used on homepage)."""
    groq = f"""
    *[_type == "post" && defined(slug.current)]
    | order(publishedAt desc)
    [0...{limit}]
    {{
        {_POST_PROJECTION}
    }}
    """
    return _query(groq)


# ---------------------------------------------------------------------------
# Resource queries
# ---------------------------------------------------------------------------

_RESOURCE_PROJECTION = """
    _id,
    title,
    slug,
    heroDescription,
    body,
    seoTitle,
    seoDescription
"""


def get_resources() -> list[dict[str, Any]]:
    """
    Fetch all resources ordered by title.
    Corresponds to documents with _type == "resource".
    """
    groq = f"""
    *[_type == "resource" && defined(slug.current)]
    | order(title asc)
    {{
        {_RESOURCE_PROJECTION}
    }}
    """
    return _query(groq)


# ---------------------------------------------------------------------------
# Interview queries
# ---------------------------------------------------------------------------

_INTERVIEW_PROJECTION = """
    _id,
    guestName,
    guestCompany,
    guestRole,
    slug,
    body,
    "guestPhoto": guestPhoto.asset->url,
    seoTitle,
    seoDescription
"""


def get_interviews() -> list[dict[str, Any]]:
    """
    Fetch all EdTech Mentor interviews.
    Corresponds to documents with _type == "interview".
    """
    groq = f"""
    *[_type == "interview" && defined(slug.current)]
    | order(guestName asc)
    {{
        {_INTERVIEW_PROJECTION}
    }}
    """
    return _query(groq)


# ---------------------------------------------------------------------------
# Category queries
# ---------------------------------------------------------------------------

def get_categories() -> list[dict[str, Any]]:
    """Return all categories."""
    groq = """
    *[_type == "category"] | order(title asc) {
        _id,
        title,
        "slug": slug.current,
        description
    }
    """
    return _query(groq)


# ---------------------------------------------------------------------------
# Settings (future)
# ---------------------------------------------------------------------------

def get_settings() -> dict[str, Any]:
    """
    Fetch the global Settings singleton document.
    Returns an empty dict if no settings document exists yet.
    This is a forward-compatible stub — the settings schema hasn't been
    created yet, but having this function here means builders can already
    call it and gracefully receive nothing.
    """
    groq = """
    *[_type == "settings"][0] {
        siteTitle,
        siteDescription,
        "logo": logo.asset->url,
        nav,
        footer,
        socialLinks,
        siteUrl,
        defaultSeoTitle,
        defaultSeoDescription,
        gaId,
        hubspotId
    }
    """
    try:
        results = _query(groq)
        # Singleton: _query returns a list, but the GROQ [0] projection
        # wraps the single doc in the result array.  Handle both shapes.
        if isinstance(results, list) and results:
            return results[0] or {}
        if isinstance(results, dict):
            return results
    except Exception:
        pass
    return {}
