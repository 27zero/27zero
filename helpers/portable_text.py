from html import escape


def render_portable_text(blocks):
    """
    Convierte Portable Text de Sanity en HTML.
    """

    if not blocks:
        return ""

    html = []

    for block in blocks:

        if block.get("_type") != "block":
            continue

        style = block.get("style", "normal")

        text = ""

        for child in block.get("children", []):

            value = escape(child.get("text", ""))

            marks = child.get("marks", [])

            if "strong" in marks:
                value = f"<strong>{value}</strong>"

            if "em" in marks:
                value = f"<em>{value}</em>"

            text += value

        if style == "h1":
            html.append(f"<h1>{text}</h1>")

        elif style == "h2":
            html.append(f"<h2>{text}</h2>")

        elif style == "h3":
            html.append(f"<h3>{text}</h3>")

        elif style == "blockquote":
            html.append(f"<blockquote>{text}</blockquote>")

        else:
            html.append(f"<p>{text}</p>")

    return "\n".join(html)