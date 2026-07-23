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
    Projection matches the fields defined in schemaTypes/settings.ts.
    All new objects are projected so templates can access nested fields
    (e.g. settings.navbar.cta.text, settings.home.hero.headline).
    """
    groq = """
    *[_type == "settings"][0] {
        siteTitle,
        siteDescription,
        siteUrl,
        "logoUrl": logo.asset->url,
        defaultSeoTitle,
        defaultSeoDescription,
        "defaultOgImageUrl": defaultOgImage.asset->url,
        gaId,
        hubspotId,
        linkedinUrl,
        twitterUrl,

        navbarCta,
        navbarWorkDropdown,

        footerCta,
        footerNavigation,
        footerCopyright,

        homeHero {
            headline,
            subtitle,
            video,
            "posterUrl": poster.asset->url
        },
        homeWork,
        homeMentor,
        homeApart,
        homeNewsletter,

        aboutHero {
            headline,
            text,
            "imageUrl": image.asset->url
        },
        aboutDna,
        aboutProofPoint {
            title,
            text,
            "imageUrl": image.asset->url
        },

        workHero,

        mentorHero,
        mentorCta,

        resourcesHero,

        contactHero,
        contactEmail,
        officeUSNew,
        officeUS,
        officeCONew,
        officeCO
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


# ---------------------------------------------------------------------------
# Work project queries
# ---------------------------------------------------------------------------

# Projection for the work index page — light, no body fields.
_WORK_INDEX_PROJECTION = """
    _id,
    title,
    "slug": slug.current,
    client,
    "clientLogo": {
        "url": clientLogo.asset->url,
        "alt": clientLogo.alt
    },
    category,
    services,
    industry,
    year,
    excerpt,
    featured,
    "order": coalesce(order, 100),
    "thumbnail": {
        "url": thumbnail.asset->url,
        "alt": thumbnail.alt
    }
"""

# Projection for detail pages — full content.
_WORK_DETAIL_PROJECTION = """
    _id,
    title,
    "slug": slug.current,
    client,
    clientTagline,
    "clientLogo": {
        "url": clientLogo.asset->url,
        "alt": clientLogo.alt
    },
    category,
    services,
    contributions,
    location,
    industry,
    year,
    excerpt,
    featured,
    description,
    brief,
    challenge,
    "solution": {
        "headline": solution.headline,
        "body":     solution.body
    },
    impact,
    "results": results[]{
        number,
        description
    },
    "testimonial": {
        "quote":      testimonial.quote,
        "authorName": testimonial.authorName,
        "authorRole": testimonial.authorRole,
        "authorPhoto": {
            "url": testimonial.authorPhoto.asset->url,
            "alt": testimonial.authorPhoto.alt
        }
    },
    "contentSections": contentSections[]{
        title,
        body,
        "images": images[]{
            "url": asset->url,
            "alt": alt
        }
    },
    "thumbnail": {
        "url": thumbnail.asset->url,
        "alt": thumbnail.alt
    },
    "heroImage": {
        "url": heroImage.asset->url,
        "alt": heroImage.alt
    },
    heroVideo,
    "gallery": gallery[]{
        "url": asset->url,
        "alt": alt,
        "caption": caption
    },
    seoTitle,
    seoDescription,
    "ogImage": {
        "url": ogImage.asset->url
    }
"""


def get_work_projects() -> list[dict]:
    """
    Fetch all work projects, ordered: featured first, then by order asc, then title.

    Returns the full projection needed for both index and detail pages.
    The caller (builders/work.py) handles splitting this list into
    index-display data and per-project detail pages.
    """
    groq = f"""
    *[_type == "workProject" && defined(slug.current)]
    | order(featured desc, coalesce(order, 100) asc, title asc)
    {{
        {_WORK_DETAIL_PROJECTION}
    }}
    """
    return _query(groq)


def get_work_categories() -> list[str]:
    """
    Return the sorted list of distinct category values present in the
    work dataset.  Used to build the filter tabs on the index page.

    Returns plain strings (the category ``value`` field), not objects,
    so the template can iterate them directly.
    """
    groq = """
    array::unique(
        *[_type == "workProject" && defined(category)].category
    )
    """
    result = _query(groq)
    # GROQ array::unique returns a list; sort it for stable rendering.
    if isinstance(result, list):
        return sorted(str(c) for c in result if c)
    return []


# ---------------------------------------------------------------------------
# Mentor interview queries
# ---------------------------------------------------------------------------

_MENTOR_PROJECTION = """
    _id,
    guestName,
    guestCompany,
    guestRole,
    "slug": slug.current,
    "guestPhoto": guestPhoto.asset->url,
    series,
    featured,
    title,
    excerpt,
    body,
    seoTitle,
    seoDescription,
    "ogImage": {
        "url": ogImage.asset->url
    }
"""


def get_mentor_interviews() -> list[dict]:
    """
    Fetch all EdTech Mentor interview documents.

    Ordered: featured first, then alphabetically by guestName.
    Corresponds to documents with _type == "interview".

    Fields used by MentorBuilder:
        guestName    — guest full name
        guestCompany — guest company
        guestRole    — guest role / title
        slug         — URL slug (string, already resolved)
        guestPhoto   — CDN URL of guest photo
        series       — series key: "essencial" | "investor" | "founders"
        featured     — bool: true for the featured card
        title        — interview headline / episode title
        excerpt      — short description shown on cards
        seoTitle, seoDescription, ogImage — SEO fields
    """
    groq = f"""
    *[_type == "interview" && defined(slug.current)]
    | order(featured desc, guestName asc)
    {{
        {_MENTOR_PROJECTION}
    }}
    """
    return _query(groq)


# ---------------------------------------------------------------------------
# Testimonial queries
# ---------------------------------------------------------------------------

def get_testimonials() -> list[dict[str, Any]]:
    """
    Fetch all featured testimonials for the home page slider.
    Ordered by the editor-defined order field.
    authorName uses coalesce: client.name takes precedence if linked.
    """
    groq = """
    *[_type == "testimonial" && featured == true]
    | order(order asc)
    {
        _id,
        quote,
        authorRole,
        featured,
        order,
        "authorName":       coalesce(client->name, authorName),
        "avatarPhotoUrl":   avatarPhoto.asset->url,
        "backgroundPhotoUrl": backgroundPhoto.asset->url,
        "clientLogoUrl":    client->logo.asset->url,
        "workSlug":         workProject->slug.current
    }
    """
    return _query(groq)


# ---------------------------------------------------------------------------
# Client queries
# ---------------------------------------------------------------------------

def get_clients() -> list[dict[str, Any]]:
    """
    Fetch all clients for the home logo strip and work marquee.
    Only returns clients with featured=true for the home strip.
    Use get_all_clients() when all clients are needed (e.g. practice page).
    """
    groq = """
    *[_type == "client" && featured == true]
    | order(logoOrder asc)
    {
        _id,
        name,
        "logoUrl":      logo.asset->url,
        "logoLightUrl": logoLight.asset->url,
        logoHeight,
        logoOrder,
        url,
        description
    }
    """
    return _query(groq)


def get_all_clients() -> list[dict[str, Any]]:
    """
    Fetch all client documents regardless of featured status.
    Used when a full client list is needed (e.g. practice brand logos).
    """
    groq = """
    *[_type == "client"]
    | order(logoOrder asc, name asc)
    {
        _id,
        name,
        "logoUrl":      logo.asset->url,
        "logoLightUrl": logoLight.asset->url,
        logoHeight,
        logoOrder,
        url,
        description
    }
    """
    return _query(groq)


# ---------------------------------------------------------------------------
# Practice queries
# ---------------------------------------------------------------------------

def get_practices() -> list[dict[str, Any]]:
    """
    Fetch all practice documents ordered by display order.
    Returns all fields needed for both the home pcard and the
    agency practices-card.
    """
    groq = """
    *[_type == "practice"]
    | order(order asc)
    {
        _id,
        title,
        "slug": slug.current,
        description,
        clientNames,
        order,
        heroHeadline,
        heroText,
        "heroImageUrl": heroImage.asset->url,
        credibilityHeadline,
        credibilityText,
        credibilityItems,
        conversationItems,
        closingCtaHeadline
    }
    """
    return _query(groq)


# ---------------------------------------------------------------------------
# Team queries
# ---------------------------------------------------------------------------

def get_team() -> list[dict[str, Any]]:
    """
    Fetch all active team members for the About page grid.
    Only returns members with active=true, ordered by display order.
    """
    groq = """
    *[_type == "teamMember" && active == true]
    | order(order asc)
    {
        _id,
        name,
        role,
        "photoUrl": photo.asset->url,
        order
    }
    """
    return _query(groq)
