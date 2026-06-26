"""
helpers/portable_text.py — Portable Text → HTML renderer.

Converts Sanity's Portable Text format into clean, semantic HTML
suitable for the 27zero article layout.

Design principles
-----------------
- Never silently discard content.  Unknown types emit an HTML comment
  so editors can spot gaps during QA without breaking the page.
- Escape all user content before inserting into HTML.
- Produce the minimum markup needed — no inline styles, no classes on
  every element.  CSS in style.css handles presentation.
- Lists are properly wrapped in <ul>/<ol>, not emitted as bare <li>.

Supported block styles
----------------------
  normal, h1, h2, h3, h4, h5, h6, blockquote

Supported inline marks
-----------------------
  strong, em, underline, strike-through, code, link

Supported non-block types
--------------------------
  image (with optional alt text and caption)

Future types (handled gracefully, logged)
------------------------------------------
  code block (custom type), callout, embed, etc.
"""

import logging
import re
from html import escape
from typing import Any

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Mark (inline annotation) rendering
# ---------------------------------------------------------------------------

def _render_mark(text: str, mark: str, mark_defs: dict[str, Any]) -> str:
    """
    Wrap ``text`` with the HTML tag corresponding to ``mark``.

    ``mark`` is either a decorator string (e.g. "strong") or the ``_key``
    of a mark definition object (e.g. a link annotation).
    """
    # Decorator marks
    if mark == "strong":
        return f"<strong>{text}</strong>"
    if mark == "em":
        return f"<em>{text}</em>"
    if mark == "underline":
        return f"<u>{text}</u>"
    if mark in ("strike-through", "strikethrough"):
        return f"<s>{text}</s>"
    if mark == "code":
        return f"<code>{text}</code>"

    # Annotation marks (key-based, look up in markDefs)
    defn = mark_defs.get(mark)
    if defn:
        mark_type = defn.get("_type", "")
        if mark_type == "link":
            href = escape(defn.get("href", "#"))
            # Open external links in a new tab.
            is_external = href.startswith("http://") or href.startswith("https://")
            attrs = f' href="{href}"'
            if is_external:
                attrs += ' target="_blank" rel="noopener noreferrer"'
            return f"<a{attrs}>{text}</a>"

    # Unknown mark — keep text but log for visibility.
    logger.warning("portable_text: unknown mark %r; rendering plain text", mark)
    return text


# ---------------------------------------------------------------------------
# Inline children rendering
# ---------------------------------------------------------------------------

def _render_children(children: list[dict], mark_defs: dict[str, Any]) -> str:
    """
    Convert a list of span children to an HTML string.

    Children are rendered in order.  Marks are applied inside-out
    (innermost mark first) to preserve correct nesting.
    """
    parts: list[str] = []

    for child in children:
        child_type = child.get("_type", "span")

        if child_type != "span":
            # Non-span inline element — log and skip for now.
            logger.warning(
                "portable_text: non-span child type %r; skipping", child_type
            )
            continue

        text = escape(child.get("text", ""))
        marks = child.get("marks", [])

        # Apply marks from innermost to outermost.
        for mark in reversed(marks):
            text = _render_mark(text, mark, mark_defs)

        parts.append(text)

    return "".join(parts)


# ---------------------------------------------------------------------------
# Block style rendering
# ---------------------------------------------------------------------------

_HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}


def _render_block(block: dict, mark_defs: dict[str, Any]) -> str:
    """Render a single block-type node to an HTML string."""
    style = block.get("style", "normal")
    children = block.get("children", [])
    inner = _render_children(children, mark_defs)

    if style in _HEADING_TAGS:
        return f"<{style}>{inner}</{style}>"

    if style == "blockquote":
        return f"<blockquote>{inner}</blockquote>"

    # Everything else (including "normal") → paragraph.
    return f"<p>{inner}</p>"


# ---------------------------------------------------------------------------
# Image rendering
# ---------------------------------------------------------------------------

def _render_image(node: dict) -> str:
    """
    Render a Portable Text image node.

    Sanity image nodes look like::

        {
          "_type": "image",
          "asset": { "_ref": "image-abc-800x600-jpg" },
          "alt": "optional alt text",
          "caption": "optional caption"
        }

    We don't resolve the ``_ref`` here because that requires an extra API
    call.  Instead we embed a ``data-sanity-ref`` attribute so tooling can
    post-process these if needed, and produce useful fallback HTML.
    """
    asset = node.get("asset", {})
    ref = asset.get("_ref", "")
    alt = escape(node.get("alt", ""))
    caption = node.get("caption", "")

    # Best-effort URL reconstruction from the asset reference.
    # Ref format: image-{id}-{dimensions}-{extension}
    url = ""
    match = re.match(r"image-([a-f0-9]+)-(\d+x\d+)-(\w+)$", ref)
    if match:
        image_id, _dims, ext = match.groups()
        from config import SANITY_CDN_URL  # imported here to avoid circular dep
        url = f"{SANITY_CDN_URL}/{image_id}.{ext}"

    if not url:
        # Asset URL was pre-resolved by the GROQ projection (preferred path).
        url = asset.get("url", "")

    if not url:
        logger.warning("portable_text: could not resolve image URL for ref %r", ref)
        return f'<!-- portable_text: unresolved image ref="{escape(ref)}" -->'

    img = f'<img src="{escape(url)}" alt="{alt}" loading="lazy"'
    if ref:
        img += f' data-sanity-ref="{escape(ref)}"'
    img += ">"

    if caption:
        return f"<figure>{img}<figcaption>{escape(caption)}</figcaption></figure>"

    return img


# ---------------------------------------------------------------------------
# List accumulation
# ---------------------------------------------------------------------------

class _ListBuffer:
    """
    Accumulates consecutive list items and flushes them as a <ul> or <ol>.

    Portable Text represents lists as a flat sequence of blocks with a
    ``listItem`` property.  We need to collect consecutive items of the
    same type and wrap them in the appropriate container.
    """

    def __init__(self) -> None:
        self._items: list[str] = []
        self._list_item: str = ""

    def start(self, list_item: str) -> None:
        self._list_item = list_item
        self._items = []

    def append(self, html: str) -> None:
        self._items.append(html)

    def active(self) -> bool:
        return bool(self._items) or bool(self._list_item)

    def same_type(self, list_item: str) -> bool:
        return list_item == self._list_item

    def flush(self) -> str:
        if not self._items:
            self._list_item = ""
            return ""
        tag = "ol" if self._list_item == "number" else "ul"
        inner = "".join(f"<li>{item}</li>" for item in self._items)
        self._items = []
        self._list_item = ""
        return f"<{tag}>{inner}</{tag}>"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def render_portable_text(blocks: list[dict] | None) -> str:
    """
    Convert a Portable Text block array to an HTML string.

    Parameters
    ----------
    blocks:
        The value of a Sanity ``blockContent`` or ``body`` field.
        May be ``None`` or an empty list (returns ``""``).

    Returns
    -------
    str
        A string of safe HTML ready to be injected via ``{{ body|safe }}``.
    """
    if not blocks:
        return ""

    html: list[str] = []
    list_buf = _ListBuffer()

    for block in blocks:
        block_type = block.get("_type")

        # ── Non-block types ──────────────────────────────────────────────
        if block_type == "image":
            # Flush any pending list before an image.
            if list_buf.active():
                html.append(list_buf.flush())
            html.append(_render_image(block))
            continue

        if block_type != "block":
            # Unknown custom block — emit a comment, keep rendering.
            if list_buf.active():
                html.append(list_buf.flush())
            logger.warning(
                "portable_text: unknown block type %r; skipping", block_type
            )
            html.append(
                f"<!-- portable_text: unsupported block type "
                f'"{escape(str(block_type))}" -->'
            )
            continue

        # ── Block type ───────────────────────────────────────────────────
        # Build a lookup dict for mark definitions (links, etc.)
        raw_mark_defs = block.get("markDefs", []) or []
        mark_defs = {d["_key"]: d for d in raw_mark_defs if "_key" in d}

        list_item = block.get("listItem")

        if list_item:
            # This block is a list item.
            if list_buf.active() and not list_buf.same_type(list_item):
                # List type changed — flush the previous list first.
                html.append(list_buf.flush())
            if not list_buf.active():
                list_buf.start(list_item)
            children_html = _render_children(block.get("children", []), mark_defs)
            list_buf.append(children_html)
        else:
            # Not a list item — flush any pending list first.
            if list_buf.active():
                html.append(list_buf.flush())
            html.append(_render_block(block, mark_defs))

    # Flush any trailing list.
    if list_buf.active():
        html.append(list_buf.flush())

    return "\n".join(html)
