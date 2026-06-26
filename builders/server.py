"""
builders/server.py — Local development HTTP server.

Extracted from build.py to keep the build orchestrator clean.

The server supports HTTP Range requests, which are required for
<video> and <audio> elements to work correctly in browsers.
Python's built-in http.server ignores Range headers entirely and
always returns the full file, which causes video elements to stall.

Usage
-----
    from builders.server import serve
    serve(port=8000)
"""

import http.server
import logging
import os
import re
import socketserver
import webbrowser

from config import DIST_DIR

logger = logging.getLogger(__name__)


class RangeHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """
    HTTP/1.1 request handler that correctly handles Range requests.

    This allows browsers to seek within video/audio files, which
    the standard SimpleHTTPRequestHandler cannot do.
    """

    # Silence the per-request log lines from SimpleHTTPRequestHandler
    # unless verbose logging is enabled; the startup message is enough.
    log_message = lambda self, *args: None  # noqa: E731

    def do_GET(self) -> None:  # noqa: N802
        path = self.translate_path(self.path)
        range_header = self.headers.get("Range")

        if range_header and os.path.isfile(path):
            self._serve_range(path, range_header)
        else:
            super().do_GET()

    def _serve_range(self, path: str, range_header: str) -> None:
        file_size = os.path.getsize(path)
        match = re.match(r"bytes=(\d*)-(\d*)", range_header)

        if not match:
            super().do_GET()
            return

        start_s, end_s = match.groups()
        start = int(start_s) if start_s else 0
        end   = int(end_s)   if end_s   else file_size - 1
        end   = min(end, file_size - 1)

        if start > end or start >= file_size:
            self.send_response(416)
            self.send_header("Content-Range", f"bytes */{file_size}")
            self.end_headers()
            return

        length = end - start + 1

        self.send_response(206)
        self.send_header("Content-type",   self.guess_type(path))
        self.send_header("Accept-Ranges",  "bytes")
        self.send_header("Content-Range",  f"bytes {start}-{end}/{file_size}")
        self.send_header("Content-Length", str(length))
        self.end_headers()

        with open(path, "rb") as fh:
            fh.seek(start)
            remaining = length
            while remaining > 0:
                chunk = fh.read(min(65_536, remaining))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    break
                remaining -= len(chunk)


def serve(port: int = 8000) -> None:
    """
    Start the development server and open the browser.

    Serves dist/ at http://localhost:{port}/.
    """
    os.chdir(DIST_DIR)
    socketserver.TCPServer.allow_reuse_address = True

    url = f"http://localhost:{port}/"
    logger.info("Serving at %s  (Ctrl+C to stop)", url)
    print(f"\nServing at {url}  (Ctrl+C to stop)\n")

    try:
        webbrowser.open(url)
    except Exception:
        pass

    with socketserver.TCPServer(("", port), RangeHTTPRequestHandler) as httpd:
        httpd.serve_forever()
