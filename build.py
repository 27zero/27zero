#!/usr/bin/env python3
"""
build.py — 27zero static site orchestrator.

This file is intentionally thin.  Its only job is to call builders
in the correct order.  All logic lives in builders/ and helpers/.

Usage
-----
    python build.py           # build only
    python build.py serve     # build then serve on :8000
    python build.py serve 3000  # build then serve on :3000
"""

import logging
import os
import shutil
import sys

from jinja2 import Environment, FileSystemLoader

from config import PAGES_DIR, TEMPLATES_DIR, ASSETS_DIR, DIST_DIR, VERBOSE

from helpers.sanity import get_posts, get_resources, get_interviews

from builders.pages   import build_pages
from builders.posts   import build_posts, build_resources, build_interviews
from builders.sitemap import build_sitemap
from builders.rss     import build_rss

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG if VERBOSE else logging.INFO,
    format="%(message)s",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def build() -> None:
    """
    Full build pipeline.

    Safety contract
    ---------------
    dist/ is NEVER cleared until every Sanity fetch has succeeded.
    A network failure or API error will abort the build before any
    existing output is destroyed.
    """

    # ── Step 1: Fetch all content from Sanity ───────────────────────────
    # If any fetch fails (network error, bad credentials, etc.) this
    # raises immediately and dist/ is untouched.
    logger.info("Fetching content from Sanity...")
    posts      = get_posts()
    resources  = get_resources()
    interviews = get_interviews()

    logger.info(
        "Loaded: %d posts, %d resources, %d interviews",
        len(posts), len(resources), len(interviews),
    )

    # ── Step 2: Clear and recreate dist/ ────────────────────────────────
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    os.makedirs(DIST_DIR)

    # ── Step 3: Configure Jinja2 ─────────────────────────────────────────
    env = Environment(
        loader=FileSystemLoader([PAGES_DIR, TEMPLATES_DIR]),
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=False,  # We escape manually; templates use |safe for HTML.
    )

    # ── Step 4: Build static pages ───────────────────────────────────────
    logger.info("\nBuilding static pages...")
    n_pages = build_pages(env, posts=posts, resources=resources)

    # ── Step 5: Build dynamic CMS pages ──────────────────────────────────
    logger.info("\nBuilding CMS content pages...")
    n_posts      = build_posts(env, posts)
    n_resources  = build_resources(env, resources)
    n_interviews = build_interviews(env, interviews)

    # ── Step 6: Generate sitemap.xml ─────────────────────────────────────
    logger.info("\nGenerating sitemap...")
    build_sitemap(posts=posts, resources=resources, interviews=interviews)

    # ── Step 7: Generate rss.xml ─────────────────────────────────────────
    logger.info("\nGenerating RSS feed...")
    build_rss(posts=posts, resources=resources)

    # ── Step 8: Copy static assets ───────────────────────────────────────
    shutil.copytree(ASSETS_DIR, os.path.join(DIST_DIR, "assets"), dirs_exist_ok=True)

    # ── Summary ──────────────────────────────────────────────────────────
    total_dynamic = n_posts + n_resources + n_interviews
    logger.info(
        "\nDone — %d static + %d CMS pages (%d posts, %d resources, %d interviews)",
        n_pages, total_dynamic, n_posts, n_resources, n_interviews,
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    build()

    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        from builders.server import serve
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
        serve(port)
