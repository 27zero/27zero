"""
config.py — 27zero site-wide configuration.

Every constant that was hardcoded in build.py now lives here.
All values support environment variable overrides so nothing
sensitive needs to be committed to version control.

Usage:
    from config import SITE_URL, DIST_DIR, SANITY_PROJECT_ID, ...
"""

import os

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
# ROOT is the directory that contains build.py and this config.py.
ROOT         = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR  = os.path.join(ROOT, "templates")
PAGES_DIR      = os.path.join(ROOT, "pages")
ASSETS_DIR     = os.path.join(ROOT, "assets")
COMPONENTS_DIR = os.path.join(ROOT, "components")
DIST_DIR       = os.path.join(ROOT, "dist")

# ---------------------------------------------------------------------------
# Site identity
# ---------------------------------------------------------------------------
SITE_URL  = os.environ.get("SITE_URL", "https://www.27zero.agency")
SITE_NAME = "27zero"
SITE_DESCRIPTION = (
    "The world's only EdTech-exclusive marketing agency. "
    "Turning purpose into brand power since 2001."
)

# ---------------------------------------------------------------------------
# Sanity CMS
# ---------------------------------------------------------------------------
# The project ID is not secret (it's in every Sanity API URL), but keeping
# it as an env var makes it easy to point at a staging dataset without
# touching source code.
SANITY_PROJECT_ID = os.environ.get("SANITY_PROJECT_ID", "qjn4zzjc")
SANITY_DATASET    = os.environ.get("SANITY_DATASET",    "production")
SANITY_API_VERSION = "2021-10-21"

# Sanity API token — required only for drafts or private datasets.
# Never commit this value; set it as a Vercel environment variable.
SANITY_TOKEN = os.environ.get("SANITY_TOKEN", "")

# Base URL for the Sanity Content Query API.
SANITY_API_URL = (
    f"https://{SANITY_PROJECT_ID}.api.sanity.io"
    f"/v{SANITY_API_VERSION}/data/query/{SANITY_DATASET}"
)

# Base URL for Sanity's image CDN (used when building image URLs).
SANITY_CDN_URL = f"https://cdn.sanity.io/images/{SANITY_PROJECT_ID}/{SANITY_DATASET}"

# ---------------------------------------------------------------------------
# Build behaviour
# ---------------------------------------------------------------------------
# When True, include draft documents in queries (requires SANITY_TOKEN).
DRAFT_MODE = os.environ.get("DRAFT_MODE", "false").lower() == "true"

# When True, additional diagnostic output is printed during the build.
VERBOSE = os.environ.get("VERBOSE", "false").lower() == "true"

# ---------------------------------------------------------------------------
# RSS / sitemap
# ---------------------------------------------------------------------------
RSS_TITLE       = f"{SITE_NAME} — EdTech Marketing Insights"
RSS_DESCRIPTION = SITE_DESCRIPTION
RSS_AUTHOR      = f"hello@27zero.agency ({SITE_NAME})"
