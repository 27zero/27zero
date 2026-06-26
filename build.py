#!/usr/bin/env python3
"""
27zero static site builder
"""

import os
import sys
import re
import shutil
import webbrowser
import http.server
import socketserver

import requests

from jinja2 import Environment, FileSystemLoader

from helpers.portable_text import render_portable_text

ROOT = os.path.dirname(os.path.abspath(__file__))

TEMPLATES_DIR = os.path.join(ROOT, "templates")
PAGES_DIR = os.path.join(ROOT, "pages")
ASSETS_DIR = os.path.join(ROOT, "assets")
DIST_DIR = os.path.join(ROOT, "dist")

SANITY_PROJECT_ID = "qjn4zzjc"
SANITY_DATASET = "production"

SANITY_API = (
    f"https://{SANITY_PROJECT_ID}.api.sanity.io"
    f"/v2021-10-21/data/query/{SANITY_DATASET}"
)


def get_posts():

    query = """
    *[_type == "post"] | order(publishedAt desc){
        title,
        slug,
        excerpt,
        publishedAt,
        body,
        seoTitle,
        seoDescription,
        featuredImage{
            "asset": {
                "url": featuredImage.asset->url
            }
        }
    }
    """

    response = requests.get(SANITY_API, params={"query": query})

    response.raise_for_status()

    return response.json().get("result", [])


PAGES = [
    ("home/index.html", ""),
    ("work/overview.html", "work"),
    ("work/anthology-marketing-programs.html", "work/anthology-marketing-programs"),
    (
        "work/ellucian-edtech-sessions-experience.html",
        "work/ellucian-edtech-sessions-experience",
    ),
    ("work/student-first.html", "work/student-first"),
    ("work/atomic-jolt-marketing-programs.html", "work/atomic-jolt-marketing-programs"),
    ("work/scholarship-magic.html", "work/scholarship-magic"),
    ("work/doctums.html", "work/doctums"),
    ("work/anthology-legacy-conversations.html", "work/anthology-legacy-conversations"),
    ("work/busuu.html", "work/busuu"),
    ("work/uplanner-customer-spotlight.html", "work/uplanner-customer-spotlight"),
    ("work/d2l-connection-cdmx.html", "work/d2l-connection-cdmx"),
    (
        "work/universidad-de-los-andes---marketing-programs.html",
        "work/universidad-de-los-andes---marketing-programs",
    ),
    ("work/d2l-edtech-sessions.html", "work/d2l-edtech-sessions"),
    ("work/uplanner-brand.html", "work/uplanner-brand"),
    ("about/overview.html", "about"),
    ("lets-talk/overview.html", "lets-talk"),
    ("resources/overview.html", "resources"),
    ("resources/edtech-marketing-agency.html", "resources/edtech-marketing-agency"),
    (
        "resources/choosing-edtech-marketing-agency.html",
        "resources/choosing-edtech-marketing-agency",
    ),
    ("resources/what-is-edtech-marketing.html", "resources/what-is-edtech-marketing"),
    (
        "resources/edtech-marketing-trends-2026.html",
        "resources/edtech-marketing-trends-2026",
    ),
    (
        "resources/edtech-marketing-operations-agency.html",
        "resources/edtech-marketing-operations-agency",
    ),
    (
        "resources/marketing-to-schools-districts.html",
        "resources/marketing-to-schools-districts",
    ),
    (
        "resources/demonstrating-impact-learning-outcomes.html",
        "resources/demonstrating-impact-learning-outcomes",
    ),
    (
        "resources/successful-edtech-website-examples.html",
        "resources/successful-edtech-website-examples",
    ),
    ("resources/edtech-websites.html", "resources/edtech-websites"),
    (
        "resources/reaching-school-decision-makers.html",
        "resources/reaching-school-decision-makers",
    ),
    (
        "resources/measuring-campaign-success.html",
        "resources/measuring-campaign-success",
    ),
    ("resources/k12-vs-higher-ed-strategy.html", "resources/k12-vs-higher-ed-strategy"),
    (
        "resources/best-ed-tech-marketing-agency.html",
        "resources/best-ed-tech-marketing-agency",
    ),
    (
        "resources/conference-lead-generation.html",
        "resources/conference-lead-generation",
    ),
    (
        "resources/overcoming-marketing-challenges.html",
        "resources/overcoming-marketing-challenges",
    ),
    ("resources/marketing-ops-challenges.html", "resources/marketing-ops-challenges"),
    ("edtech-mentor/overview.html", "edtech-mentor-interviews"),
    ("edtech-mentor/frederico-bello.html", "edtech-mentor-interviews/frederico-bello"),
    ("edtech-marketing/overview.html", "edtech-marketing-agency"),
    (
        "edtech-marketing/customer-marketing.html",
        "edtech-marketing-agency/customer-marketing",
    ),
    (
        "edtech-marketing/granular-marketing-programs.html",
        "edtech-marketing-agency/granular-marketing-programs",
    ),
    (
        "edtech-marketing/agile-brand-development.html",
        "edtech-marketing-agency/agile-brand-development",
    ),
    (
        "edtech-marketing/thought-leadership-executive-content.html",
        "edtech-marketing-agency/thought-leadership-executive-content",
    ),
    (
        "edtech-marketing/video-motion-editorial-content.html",
        "edtech-marketing-agency/video-motion-editorial-content",
    ),
    (
        "edtech-marketing/gtm-playbooks-launch-campaigns.html",
        "edtech-marketing-agency/gtm-playbooks-launch-campaigns",
    ),
    (
        "edtech-marketing/marketing-operations-crm.html",
        "edtech-marketing-agency/marketing-operations-crm",
    ),
    (
        "edtech-marketing/market-research-audience-insights.html",
        "edtech-marketing-agency/market-research-audience-insights",
    ),
    (
        "edtech-marketing/events-experiences.html",
        "edtech-marketing-agency/events-experiences",
    ),
    (
        "edtech-marketing/performance-marketing-paid-media.html",
        "edtech-marketing-agency/performance-marketing-paid-media",
    ),
    (
        "edtech-marketing/brand-identity-design.html",
        "edtech-marketing-agency/brand-identity-design",
    ),
    (
        "edtech-marketing/website-design-ux.html",
        "edtech-marketing-agency/website-design-ux",
    ),
]


def build():

    env = Environment(
        loader=FileSystemLoader([PAGES_DIR, TEMPLATES_DIR]),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)

    os.makedirs(DIST_DIR)

    posts = get_posts()

    print(f"Loaded {len(posts)} posts from Sanity")

    #
    # Páginas estáticas
    #

    for template_path, url_path in PAGES:

        template = env.get_template(template_path)

        html = template.render(posts=posts)

        out_dir = DIST_DIR if url_path == "" else os.path.join(DIST_DIR, url_path)

        os.makedirs(out_dir, exist_ok=True)

        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)
            print(f"built /{url_path}/" if url_path else "built /")

    #
    # Generar automáticamente una página por cada post de Sanity
    #

    post_template = env.get_template("resources/post.html")

    for post in posts:

        body_html = render_portable_text(post.get("body", []))

        html = post_template.render(post=post, body_html=body_html)

        slug = post["slug"]["current"]

        out_dir = os.path.join(DIST_DIR, "resources", slug)

        os.makedirs(out_dir, exist_ok=True)

        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html)

        print(f"built /resources/{slug}/")

    #
    # Copiar assets
    #

    shutil.copytree(ASSETS_DIR, os.path.join(DIST_DIR, "assets"), dirs_exist_ok=True)

    print(f"\nDone — {len(PAGES)} static pages + {len(posts)} blog posts")


class RangeHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):

        path = self.translate_path(self.path)
        range_header = self.headers.get("Range")

        if range_header and os.path.isfile(path):
            self._serve_range(path, range_header)
        else:
            super().do_GET()

    def _serve_range(self, path, range_header):

        file_size = os.path.getsize(path)

        m = re.match(r"bytes=(\d*)-(\d*)", range_header)

        if not m:
            super().do_GET()
            return

        start_s, end_s = m.groups()

        start = int(start_s) if start_s else 0
        end = int(end_s) if end_s else file_size - 1

        end = min(end, file_size - 1)

        if start > end or start >= file_size:

            self.send_response(416)

            self.send_header("Content-Range", f"bytes */{file_size}")

            self.end_headers()
            return

        length = end - start + 1

        self.send_response(206)

        self.send_header("Content-type", self.guess_type(path))

        self.send_header("Accept-Ranges", "bytes")

        self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")

        self.send_header("Content-Length", str(length))

        self.end_headers()

        with open(path, "rb") as f:

            f.seek(start)

            remaining = length

            while remaining > 0:

                chunk = f.read(min(65536, remaining))

                if not chunk:
                    break

                try:
                    self.wfile.write(chunk)

                except (BrokenPipeError, ConnectionResetError):
                    break

                remaining -= len(chunk)


def serve(port=8000):

    os.chdir(DIST_DIR)

    socketserver.TCPServer.allow_reuse_address = True

    with socketserver.TCPServer(("", port), RangeHTTPRequestHandler) as httpd:

        url = f"http://localhost:{port}/"

        print(f"\nServing at {url}")

        try:
            webbrowser.open(url)
        except Exception:
            pass

        httpd.serve_forever()


if __name__ == "__main__":

    build()

    if len(sys.argv) > 1 and sys.argv[1] == "serve":

        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000

        serve(port)
