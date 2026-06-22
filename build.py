#!/usr/bin/env python3
"""
27zero static site builder.

Renders the Jinja2 templates in pages/ into flat, static HTML files in dist/,
using the shared layout and components in templates/base.html and templates/macros.html.

USAGE
    python3 build.py            Build the site into dist/
    python3 build.py serve      Build, then serve dist/ locally and open it in your browser
    python3 build.py serve 8080 Same, on a specific port (default is 8000)

ADDING A NEW PAGE
    1. Create a new .html file under pages/<section>/ that starts with:
           {% extends "base.html" %}
           {% from "macros.html" import hero, cta_footer, ... %}
           {% block title %}Page Title — 27zero{% endblock %}
           {% block content %}
           ...your page content, using the shared macros where useful...
           {% endblock %}
    2. Add one line to the PAGES list below: (template path, output URL path)
    3. Run this script again. dist/ is rebuilt from scratch every run.

DEPLOYING
    The dist/ folder is a complete, ready-to-publish static site — every page
    is plain HTML, every internal link is root-relative (e.g. /edtech-marketing-agency/...),
    and assets/css/style.css is the one stylesheet every page shares.
    Upload dist/ as-is to any static host (Netlify, Vercel, GitHub Pages, Cloudflare
    Pages, or a plain web server's document root) and the site is live.

    Root-relative links mean dist/ needs to be served by something — even
    locally — rather than opened directly as a file:// page. `python3 build.py
    serve` handles that for previewing on your own machine.
"""
import os
import sys
import re
import shutil
import webbrowser
import http.server
import socketserver
from jinja2 import Environment, FileSystemLoader

ROOT = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(ROOT, "templates")
PAGES_DIR = os.path.join(ROOT, "pages")
ASSETS_DIR = os.path.join(ROOT, "assets")
DIST_DIR = os.path.join(ROOT, "dist")

# Each entry: (template path relative to pages/, output URL path relative to site root)
# Output becomes dist/<url path>/index.html, served at /<url path>/ with no .html in the URL.
# Use "" as the url path for the homepage once it's rebuilt.
PAGES = [
    # --- Home ---
    ("home/index.html", ""),

    # --- Work ---
    ("work/overview.html", "work"),
    ("work/anthology-marketing-programs.html", "work/anthology-marketing-programs"),
    ("work/ellucian-edtech-sessions-experience.html", "work/ellucian-edtech-sessions-experience"),
    ("work/student-first.html", "work/student-first"),
    ("work/atomic-jolt-marketing-programs.html", "work/atomic-jolt-marketing-programs"),
    ("work/scholarship-magic.html", "work/scholarship-magic"),
    ("work/doctums.html", "work/doctums"),
    ("work/anthology-legacy-conversations.html", "work/anthology-legacy-conversations"),
    ("work/busuu.html", "work/busuu"),
    ("work/uplanner-customer-spotlight.html", "work/uplanner-customer-spotlight"),
    ("work/d2l-connection-cdmx.html", "work/d2l-connection-cdmx"),
    ("work/universidad-de-los-andes---marketing-programs.html", "work/universidad-de-los-andes---marketing-programs"),
    ("work/d2l-edtech-sessions.html", "work/d2l-edtech-sessions"),
    ("work/uplanner-brand.html", "work/uplanner-brand"),

    # --- About ---
    ("about/overview.html", "about"),

    # --- Let's Talk ---
    ("lets-talk/overview.html", "lets-talk"),

    # --- Resources ---
    ("resources/overview.html", "resources"),
    ("resources/edtech-marketing-agency.html", "resources/edtech-marketing-agency"),
    ("resources/choosing-edtech-marketing-agency.html", "resources/choosing-edtech-marketing-agency"),
    ("resources/what-is-edtech-marketing.html", "resources/what-is-edtech-marketing"),
    ("resources/edtech-marketing-trends-2026.html", "resources/edtech-marketing-trends-2026"),
    ("resources/edtech-marketing-operations-agency.html", "resources/edtech-marketing-operations-agency"),
    ("resources/marketing-to-schools-districts.html", "resources/marketing-to-schools-districts"),
    ("resources/demonstrating-impact-learning-outcomes.html", "resources/demonstrating-impact-learning-outcomes"),
    ("resources/successful-edtech-website-examples.html", "resources/successful-edtech-website-examples"),
    ("resources/edtech-websites.html", "resources/edtech-websites"),
    ("resources/reaching-school-decision-makers.html", "resources/reaching-school-decision-makers"),
    ("resources/measuring-campaign-success.html", "resources/measuring-campaign-success"),
    ("resources/k12-vs-higher-ed-strategy.html", "resources/k12-vs-higher-ed-strategy"),
    ("resources/best-ed-tech-marketing-agency.html", "resources/best-ed-tech-marketing-agency"),
    ("resources/conference-lead-generation.html", "resources/conference-lead-generation"),
    ("resources/overcoming-marketing-challenges.html", "resources/overcoming-marketing-challenges"),
    ("resources/marketing-ops-challenges.html", "resources/marketing-ops-challenges"),

    # --- The EdTech Mentor (hub + first published interview; ~65 more in backlog, see README) ---
    ("edtech-mentor/overview.html", "edtech-mentor-interviews"),
    ("edtech-mentor/frederico-bello.html", "edtech-mentor-interviews/frederico-bello"),

    # --- EdTech Marketing section (rebuilt) ---
    ("edtech-marketing/overview.html", "edtech-marketing-agency"),
    ("edtech-marketing/customer-marketing.html", "edtech-marketing-agency/customer-marketing"),
    ("edtech-marketing/granular-marketing-programs.html", "edtech-marketing-agency/granular-marketing-programs"),
    ("edtech-marketing/agile-brand-development.html", "edtech-marketing-agency/agile-brand-development"),
    ("edtech-marketing/thought-leadership-executive-content.html", "edtech-marketing-agency/thought-leadership-executive-content"),
    ("edtech-marketing/video-motion-editorial-content.html", "edtech-marketing-agency/video-motion-editorial-content"),
    ("edtech-marketing/gtm-playbooks-launch-campaigns.html", "edtech-marketing-agency/gtm-playbooks-launch-campaigns"),
    ("edtech-marketing/marketing-operations-crm.html", "edtech-marketing-agency/marketing-operations-crm"),
    ("edtech-marketing/market-research-audience-insights.html", "edtech-marketing-agency/market-research-audience-insights"),
    ("edtech-marketing/events-experiences.html", "edtech-marketing-agency/events-experiences"),
    ("edtech-marketing/performance-marketing-paid-media.html", "edtech-marketing-agency/performance-marketing-paid-media"),
    ("edtech-marketing/brand-identity-design.html", "edtech-marketing-agency/brand-identity-design"),
    ("edtech-marketing/website-design-ux.html", "edtech-marketing-agency/website-design-ux"),

    # --- Future: remaining ~65 EdTech Mentor interviews, added one at a time as built ---
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

    for template_path, url_path in PAGES:
        template = env.get_template(template_path)
        html = template.render()
        out_dir = os.path.join(DIST_DIR, url_path) if url_path else DIST_DIR
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, "index.html")
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"  built /{url_path}/" if url_path else "  built / (home)")

    shutil.copytree(ASSETS_DIR, os.path.join(DIST_DIR, "assets"), dirs_exist_ok=True)

    print(f"\nDone — {len(PAGES)} pages built to dist/")


class RangeHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Adds basic HTTP Range support on top of SimpleHTTPRequestHandler.
    Needed for <video>/<audio> elements, which request byte ranges to
    determine duration and begin playback — plain SimpleHTTPRequestHandler
    ignores Range headers entirely and always returns the whole file,
    which leaves <video> stuck never loading metadata."""

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
    handler = RangeHTTPRequestHandler
    # Avoid "Address already in use" errors when restarting quickly
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), handler) as httpd:
        url = f"http://localhost:{port}/"
        print(f"\nServing at {url}")
        print("Press Ctrl+C to stop.\n")
        try:
            webbrowser.open(url)
        except Exception:
            pass
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    build()
    if len(sys.argv) > 1 and sys.argv[1] == "serve":
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
        serve(port)
