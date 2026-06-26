"""
helpers/images.py — Sanity Image CDN URL builder.

Sanity images are served through the Sanity Image CDN (cdn.sanity.io),
which supports a rich query-string API for resizing, cropping, format
conversion, and quality control.

This module provides a single ``image_url()`` function that builds the
correct URL from a Sanity image asset reference or pre-resolved URL.

Reference: https://www.sanity.io/docs/image-urls

Usage
-----
    from helpers.images import image_url

    src = image_url(post["featuredImage"]["url"], width=800, auto="format")
    srcset = responsive_srcset(post["featuredImage"]["url"], [400, 800, 1200])
"""

import re
from urllib.parse import urlencode, urlparse, urlunparse, parse_qs, urlencode

from config import SANITY_CDN_URL, SANITY_PROJECT_ID, SANITY_DATASET


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _ref_to_url(ref: str) -> str:
    """
    Convert a Sanity image asset ``_ref`` to a CDN URL.

    Asset refs look like: ``image-abc123def-1920x1080-jpg``
    CDN URL pattern:      ``https://cdn.sanity.io/images/{project}/{dataset}/{id}.{ext}``
    """
    match = re.match(r"^image-([a-f0-9]+)-\d+x\d+-(\w+)$", ref)
    if not match:
        return ""
    image_id, ext = match.groups()
    return f"{SANITY_CDN_URL}/{image_id}.{ext}"


def _add_params(base_url: str, params: dict) -> str:
    """Append query parameters to a URL, merging with any existing ones."""
    if not params:
        return base_url
    # Strip empty values.
    clean = {k: str(v) for k, v in params.items() if v is not None and str(v)}
    if not clean:
        return base_url
    sep = "&" if "?" in base_url else "?"
    return base_url + sep + urlencode(clean)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def image_url(
    source: str | dict | None,
    *,
    width: int | None = None,
    height: int | None = None,
    quality: int | None = None,
    auto: str | None = "format",
    fit: str | None = None,
    crop: str | None = None,
) -> str:
    """
    Build a Sanity CDN image URL with optional transformations.

    Parameters
    ----------
    source:
        Either:
        - A string CDN URL (e.g. already resolved by GROQ ``asset->url``)
        - A string ``_ref`` (e.g. ``"image-abc123-800x600-jpg"``)
        - A dict with a ``"url"`` key (as returned by helpers/sanity.py)
        - ``None`` → returns ``""``

    width, height:
        Pixel dimensions.  Sanity maintains aspect ratio when only one is given.
    quality:
        JPEG/WebP quality 0–100.  Default (None) lets Sanity use its default (75).
    auto:
        ``"format"`` lets Sanity pick WebP/AVIF for supporting browsers.
        Set to ``None`` to disable.
    fit:
        Resize mode: ``"crop"``, ``"fill"``, ``"min"``, ``"max"``, ``"scale"``.
    crop:
        Crop anchor: ``"center"``, ``"top"``, ``"focalpoint"``, etc.

    Returns
    -------
    str
        A complete, ready-to-use image URL, or ``""`` if source is empty.
    """
    if not source:
        return ""

    # Resolve source to a base URL string.
    if isinstance(source, dict):
        base = source.get("url", "")
    elif source.startswith("image-"):
        base = _ref_to_url(source)
    else:
        base = source

    if not base:
        return ""

    params: dict[str, str | int] = {}
    if width:
        params["w"] = width
    if height:
        params["h"] = height
    if quality:
        params["q"] = quality
    if auto:
        params["auto"] = auto
    if fit:
        params["fit"] = fit
    if crop:
        params["crop"] = crop

    return _add_params(base, params)


def responsive_srcset(
    source: str | dict | None,
    widths: list[int] | None = None,
    **kwargs,
) -> str:
    """
    Build a ``srcset`` attribute value for responsive images.

    Example::

        srcset="{{ image_srcset(post.featuredImage.url, [400, 800, 1200]) }}"

    Parameters
    ----------
    source:
        Same as ``image_url()``.
    widths:
        List of pixel widths to include.  Defaults to ``[640, 1280, 1920]``.
    **kwargs:
        Forwarded to ``image_url()`` (e.g. ``quality=80``).

    Returns
    -------
    str
        A ``srcset`` value like ``"…?w=400 400w, …?w=800 800w"``.
    """
    if widths is None:
        widths = [640, 1280, 1920]

    parts = [
        f"{image_url(source, width=w, **kwargs)} {w}w"
        for w in widths
    ]
    return ", ".join(parts)
