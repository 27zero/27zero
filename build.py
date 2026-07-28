#!/usr/bin/env python3
"""
build.py — 27zero static site build orchestrator.

This file is intentionally thin.  Its only responsibility is to call
helpers and builders in the correct order.  All content logic lives in
helpers/.  All page-generation logic lives in builders/.

Safety contract
---------------
dist/ is never cleared until every Sanity fetch has succeeded.
If any fetch raises (network error, API outage, bad credentials),
the build aborts before touching the existing dist/.  The last
successful build stays live.

Adding a new CMS section
------------------------
1. Add a get_{section}() function to helpers/sanity.py.
2. Create builders/{section}.py — subclass SectionBuilder, set class
   attributes, override body_html() if the section has portable-text
   fields.  See builders/work.py as the reference implementation.
3. Add pages/{section}/index.html and pages/{section}/detail.html.
4. In build() below:
     a. Import and call get_{section}().
     b. Instantiate the builder and call .build(env, items).
     c. Append (builder_instance, items) to section_builders.

Nothing else changes.  Sitemap entries, SEO, and file layout are
handled automatically by SectionBuilder.

Usage
-----
    python build.py            # build only
    python build.py serve      # build then serve at http://localhost:8000
    python build.py serve 3000 # build then serve on a custom port
"""

import logging
import os
import shutil
import sys

from jinja2 import Environment, FileSystemLoader

from config import PAGES_DIR, TEMPLATES_DIR, ASSETS_DIR, COMPONENTS_DIR, DIST_DIR, VERBOSE

from helpers.sanity import (
    get_posts,
    get_resources,
    get_interviews,
    get_work_projects,
    get_mentor_interviews,
    get_settings,
    get_testimonials,
    get_clients,
    get_practices,
    get_team,
)

from builders.pages   import build_pages
from builders.posts   import build_posts, build_resources, build_interviews
from builders.work    import WorkBuilder
from builders.mentor  import MentorBuilder
from builders.sitemap import build_sitemap
from builders.rss     import build_rss

# ---------------------------------------------------------------------------
# Logging
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
    """Run the complete build pipeline."""

    # ── Step 1: Fetch all content from Sanity ───────────────────────────
    # All fetches happen before dist/ is modified.
    logger.info("Fetching content from Sanity...")
    posts      = get_posts()
    resources  = get_resources()
    interviews = get_interviews()
    work       = get_work_projects()
    mentors    = get_mentor_interviews()
    settings     = get_settings()
    testimonials = get_testimonials()
    clients      = get_clients()
    practices    = get_practices()
    team         = get_team()

    logger.info(
        "Loaded: %d posts, %d resources, %d interviews, %d work projects, %d mentor interviews",
        len(posts), len(resources), len(interviews), len(work), len(mentors),
    )
    logger.info(
        "Loaded: %d testimonials, %d clients, %d practices, %d team members",
        len(testimonials), len(clients), len(practices), len(team),
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
        autoescape=False,  # Content is escaped manually; templates use |safe.
    )

    # ── Step 4: Static pages ─────────────────────────────────────────────
    logger.info("\nBuilding static pages...")
    n_pages = build_pages(
        env,
        posts=posts,
        resources=resources,
        work=work,
        mentors=mentors,
        settings=settings,
        testimonials=testimonials,
        clients=clients,
        practices=practices,
        team=team,
    )

    # ── Step 5: Legacy CMS builders ──────────────────────────────────────
    # Posts, resources, and interviews use builders/posts.py, which predates
    # SectionBuilder.  They continue to work unchanged.  They will migrate
    # to SectionBuilder when their templates are redesigned.
    logger.info("\nBuilding CMS content pages...")
    n_posts      = build_posts(env, posts)
    n_resources  = build_resources(env, resources)
    n_interviews = build_interviews(env, interviews)

    # ── Step 6: SectionBuilder sections ──────────────────────────────────
    logger.info("\nBuilding Work section...")
    work_builder = WorkBuilder()
    n_work = work_builder.build(env, work)

    logger.info("\nBuilding EdTech Mentor section...")
    mentor_builder = MentorBuilder()
    n_mentor = mentor_builder.build(env, mentors)

    # section_builders is the list of (builder_instance, items) pairs that
    # the sitemap uses to collect URLs.  Add new sections here as they are
    # built — that is the only change required to the sitemap.
    section_builders = [
        (work_builder,   work),
        (mentor_builder, mentors),
    ]

    # ── Step 7: Sitemap ───────────────────────────────────────────────────
    logger.info("\nGenerating sitemap...")
    build_sitemap(
        section_builders=section_builders,
        legacy_entries={
            "posts":      posts,
            "resources":  resources,
            "interviews": interviews,
        },
    )

    # ── Step 8: RSS feed ──────────────────────────────────────────────────
    logger.info("\nGenerating RSS feed...")
    build_rss(posts=posts, resources=resources)

    # ── Step 9: Copy browser-served static trees ─────────────────────────
    # CSS lives in assets/css/ and is served via copytree(ASSETS_DIR) below.
    # JavaScript that lives in pages/ and is fetched at a different URL path
    # must be listed explicitly in _page_assets.
    shutil.copytree(ASSETS_DIR, os.path.join(DIST_DIR, "assets"), dirs_exist_ok=True)
    shutil.copytree(COMPONENTS_DIR, os.path.join(DIST_DIR, "components"), dirs_exist_ok=True)

    # Page-level JavaScript: source lives in pages/ but is served at a URL
    # that does not match the source path. Each tuple: (source, dist_dest).
    _page_assets = [
        # /resources/script.js — TOC active-link logic for resources pages
        (os.path.join(PAGES_DIR, "resources", "script.js"),
         os.path.join(DIST_DIR, "resources", "script.js")),
        # /work/script.js — pill filter + slider logic (source: pages/clientes/script.js)
        (os.path.join(PAGES_DIR, "clientes", "script.js"),
         os.path.join(DIST_DIR, "work", "script.js")),
        # /edtech-mentor-cms/script.js — CMS detail page interactions
        (os.path.join(PAGES_DIR, "edtech-mentor", "edtech-mentor-cms", "script.js"),
         os.path.join(DIST_DIR, "edtech-mentor-cms", "script.js")),
        # /edtech-mentor/script.js — mentor index page interactions
        (os.path.join(PAGES_DIR, "edtech-mentor", "script.js"),
         os.path.join(DIST_DIR, "edtech-mentor", "script.js")),
    ]
    for _src, _dst in _page_assets:
        if os.path.exists(_src):
            os.makedirs(os.path.dirname(_dst), exist_ok=True)
            shutil.copy2(_src, _dst)

    # ── Summary ───────────────────────────────────────────────────────────
    total_dynamic = n_posts + n_resources + n_interviews + n_work + n_mentor
    logger.info(
        "\nDone — %d static + %d CMS pages "
        "(%d posts, %d resources, %d interviews, %d work, %d mentor)",
        n_pages, total_dynamic,
        n_posts, n_resources, n_interviews, n_work, n_mentor,
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