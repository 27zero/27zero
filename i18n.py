"""
helpers/i18n.py — Multilingual support for the 27zero static build.

Locale model
------------
Three locales are supported:

    en-us   North America — served at /
    en-eu   Europe        — served at /eu/
    es-419  Latin America — served at /es/

The canonical locale is ``en-us``.  Its URL prefix is the empty string,
meaning all existing URLs stay unchanged.  ``en-eu`` and ``es-419``
are served under /eu/ and /es/ respectively.

Content lives in content/{locale}/site.json.  Each file is a dict that
templates receive as the ``i18n`` context variable.

Adding a new locale
-------------------
1. Add an entry to LOCALES below.
2. Create content/{locale_key}/site.json with the same keys as the others.
   No other file needs to change.
"""

import json
import os
from typing import Any

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT_DIR = os.path.join(ROOT, "content")

# ---------------------------------------------------------------------------
# Locale registry — single source of truth
# ---------------------------------------------------------------------------

LOCALES: list[dict[str, str]] = [
    # key: matches the content/ subdirectory name
    # prefix: URL prefix (empty = root /)
    # hreflang: value used in <link rel="alternate" hreflang="...">
    {"key": "en-us",  "prefix": "",   "hreflang": "en-US"},
    {"key": "en-eu",  "prefix": "eu", "hreflang": "en-GB"},
    {"key": "es-419", "prefix": "es", "hreflang": "es-419"},
]

# Canonical locale (x-default)
DEFAULT_LOCALE = LOCALES[0]


# ---------------------------------------------------------------------------
# Content loading
# ---------------------------------------------------------------------------

def load_locale(locale_key: str) -> dict[str, Any]:
    """
    Load and return the site.json content dict for ``locale_key``.

    Raises FileNotFoundError if the file does not exist.
    """
    path = os.path.join(CONTENT_DIR, locale_key, "site.json")
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def load_all_locales() -> list[dict[str, Any]]:
    """Return a list of content dicts, one per locale, in LOCALES order."""
    return [load_locale(loc["key"]) for loc in LOCALES]


# ---------------------------------------------------------------------------
# URL helpers
# ---------------------------------------------------------------------------

def prefix_url(url_path: str, prefix: str) -> str:
    """
    Prepend a locale prefix to a url_path.

    Examples:
        prefix_url("about", "eu")   → "eu/about"
        prefix_url("about", "")     → "about"
        prefix_url("", "eu")        → "eu"
        prefix_url("", "")          → ""
    """
    if not prefix:
        return url_path
    if not url_path:
        return prefix
    return f"{prefix}/{url_path}"


def hreflang_links(url_path: str, site_url: str) -> str:
    """
    Return a block of <link rel="alternate" hreflang="..."> tags for a page.

    Includes x-default pointing at the canonical (en-us) URL.

    Parameters
    ----------
    url_path:
        The locale-neutral url_path (e.g. "about", "resources").
        The function prepends each locale's prefix automatically.
    site_url:
        Absolute site root, e.g. "https://www.27zero.agency".
    """
    lines: list[str] = []
    for loc in LOCALES:
        prefixed = prefix_url(url_path, loc["prefix"])
        abs_url  = f"{site_url}/{prefixed}/" if prefixed else f"{site_url}/"
        lines.append(
            f'<link rel="alternate" hreflang="{loc["hreflang"]}" href="{abs_url}">'
        )
    # x-default points at the canonical (en-us) URL
    default_prefixed = prefix_url(url_path, DEFAULT_LOCALE["prefix"])
    default_url      = f"{site_url}/{default_prefixed}/" if default_prefixed else f"{site_url}/"
    lines.append(
        f'<link rel="alternate" hreflang="x-default" href="{default_url}">'
    )
    return "\n".join(lines)
