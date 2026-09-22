#!/usr/bin/env python3
"""One-shot: migrate every old-format blog post to the new body format.

Deterministic transforms (same rules for every file):
  1. Merge <h1> + h2.subtitle into a single <h1>Title: Subtitle</h1>
  2. Replace h3.subtitle "Epistemic status" with div.epistemic ES in .center
  3. Collapse .center to one date line (D Mon YYYY - N min read), drop
     words count / Other posts / Failure resume links
  4. Move commented <details class="toc-details"> after the TL;DR, remove
     the active <section class="toc">
  5. Comment out footer.js
  6. Strip ■ from content <h2> link text
  7. Rewrite h3 tree symbols: within each parent group, all but last = ├─,
     last = └─
  8. Remove trailing <hr> before </div>
  9. Remove standalone <br> between block elements
 10. Update <title>, og:title, JSON-LD headline to the new h1

After running: gen_feed.py + check_site.py + Blog_pages link text sync.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "blogPosts"
SKIP = {"_template.html", "August Monthly Business Ahas.html"}

ES_URL = (
    "https://forum.effectivealtruism.org/posts/bbtvDJtb6YwwWtJm7/"
    "epistemic-status-an-explainer-and-some-thoughts"
)

MONTHS = {
    "January": "Jan", "February": "Feb", "March": "Mar", "April": "Apr",
    "May": "May", "June": "Jun", "July": "Jul", "August": "Aug",
    "September": "Sep", "October": "Oct", "November": "Nov", "December": "Dec",
}

TOC_COMMENTED = """        <!-- TOC disabled for now — uncomment to restore the expandable TOC.
             toc.js is a no-op while this stays commented out. -->
        <!--
        <details class="toc-details">
            <summary>TOC</summary>
        </details>
        -->
"""

FOOTER_COMMENTED = """    <!-- Footer disabled for now — uncomment to restore. -->
    <!--
    <script src="../javascript/footer.js"></script>
    -->
"""


def abbrev_date(raw: str) -> str:
    """'1 February 2026' -> '1 Feb 2026'; 'August 2026' -> 'Aug 2026'."""
    raw = raw.strip()
    for full, abbr in MONTHS.items():
        if full in raw:
            return raw.replace(full, abbr)
    return raw


def parent_id(hid: str) -> str:
    """h1.2.1 -> h1.2 ; h1.2.2.1a -> h1.2.2.1 ; h1.1 -> h1."""
    if not hid:
        return ""
    parts = hid.split(".")
    last = parts[-1]
    m = re.match(r"^(\d+)([a-z]+)$", last, re.I)
    if m:
        return ".".join(parts[:-1] + [m.group(1)])
    return ".".join(parts[:-1])


def rewrite_h3_tree(text: str) -> str:
    """Assign ├─ / └─ per sibling group (shared parent_id)."""
    # Collect content h3 blocks: <h3 id="..."> ... <a ...>SYM title</a> ... </h3>
    pattern = re.compile(
        r'(<h3\s+id="([^"]+)"[^>]*>\s*<a\s+href="[^"]*">)([├└]─\s*)?([^<]*)(</a>)',
        re.S,
    )
    matches = list(pattern.finditer(text))
    if not matches:
        return text

    groups: dict[str, list[re.Match]] = {}
    for m in matches:
        groups.setdefault(parent_id(m.group(2)), []).append(m)

    # Build replacement map id -> symbol
    symbols: dict[str, str] = {}
    for _parent, group in groups.items():
        for i, m in enumerate(group):
            symbols[m.group(2)] = "└─ " if i == len(group) - 1 else "├─ "

    def repl(m: re.Match) -> str:
        sym = symbols.get(m.group(2), "├─ ")
        return f"{m.group(1)}{sym}{m.group(4)}{m.group(5)}"

    return pattern.sub(repl, text)


def strip_h2_square(text: str) -> str:
    # Only inside content h2 links (have href="#..."), not .subtitle
    return re.sub(
        r'(<h2[^>]*>\s*<a\s+href="#[^"]*">)\s*■\s*',
        r"\1",
        text,
    )


def remove_trailing_hr(text: str) -> str:
    return re.sub(r"\s*<hr>\s*(?=</div>\s*</main>)", "\n", text)


def remove_block_stray_br(text: str) -> str:
    text = re.sub(r"</p>\s*<br>\s*(?=<p\b)", "</p>\n        ", text)
    text = re.sub(r"</section>\s*<br>\s*(?=<)", "</section>\n        ", text)
    text = re.sub(r"</ul>\s*<br>\s*(?=<)", "</ul>\n        ", text)
    text = re.sub(r"</div>\s*<br>\s*(?=<)", "</div>\n        ", text)
    return text


def comment_footer(text: str) -> str:
    # Active footer (possibly odd indent)
    text = re.sub(
        r'[ \t]*<script src="\.\./javascript/footer\.js"></script>\s*',
        FOOTER_COMMENTED,
        text,
        count=1,
    )
    return text


def extract_h2_subtitle(text: str) -> tuple[str, str | None, str]:
    """Return (rest, subtitle_html_or_None, extra_id_or_None)."""
    m = re.search(r'[ \t]*<h2 class="subtitle"([^>]*)>(.*?)</h2>\s*\n', text, re.S)
    if not m:
        return text, None, ""
    attrs, inner = m.group(1), m.group(2)
    id_m = re.search(r'id="([^"]+)"', attrs)
    extra_id = id_m.group(1) if id_m else ""
    rest = text[: m.start()] + text[m.end():]
    return rest, inner.strip(), extra_id


def extract_h3_subtitle(text: str) -> tuple[str, str | None]:
    m = re.search(
        r'[ \t]*<h3 class="subtitle">.*?Epistemic status</a>:\s*(.*?)</h3>\s*\n',
        text,
        re.S,
    )
    if not m:
        return text, None
    body = m.group(1).strip()
    # body is like <i>...</i> — keep inner text wrapped in <i>
    rest = text[: m.start()] + text[m.end():]
    return rest, body


def extract_center(text: str) -> tuple[str, dict]:
    # Old .center is a wrapper around non-nested child divs; match children first
    # so the closing </div> is the outer one, not the first child's.
    m = re.search(
        r"([ \t]*)<div class=\"center\">\s*\n"
        r"((?:[ \t]*<div[^>]*>.*?</div>\s*\n)+)"
        r"[ \t]*</div>\s*\n",
        text,
        re.S,
    )
    if not m:
        return text, {}
    indent = m.group(1)
    children = m.group(2)
    divs = re.findall(r"<div[^>]*>(.*?)</div>", children, re.S)
    rest = text[: m.start()] + text[m.end():]
    info = {"divs": [d.strip() for d in divs], "indent": indent}
    return rest, info


def strip_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s)


def build_center(indent: str, date_raw: str, length_raw: str, es_body: str | None) -> str:
    date_a = abbrev_date(strip_tags(date_raw))
    # length_raw: '1200 words - 5 min read' or '~3400 words - 15 min read'
    min_m = re.search(r"(\d+)\s*min read", strip_tags(length_raw))
    mins = min_m.group(1) if min_m else None
    if mins:
        meta = f"{date_a} - {mins} min read"
    else:
        # e.g. 'August 2026' only, or words without min — keep date + try extract
        meta = date_a
        if "min read" in strip_tags(length_raw):
            # fallback: keep full length string cleaned
            meta = f"{date_a} - {strip_tags(length_raw)}"
    lines = [f"{indent}<div><em>{meta}</em></div>"]
    if es_body:
        lines.append(
            f'{indent}<div class="epistemic"><a\n'
            f'{indent}        href="{ES_URL}"\n'
            f'{indent}        target="_blank"><em>ES</em></a>: {es_body}</div>'
        )
    return f'{indent}<div class="center">\n' + "\n".join(lines) + f"\n{indent}</div>\n"


def xml_text(s: str) -> str:
    """Escape for HTML text/attrs without turning ' into &#x27; (breaks
    check_site title/h1 comparison)."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def update_head_titles(text: str, new_h1: str) -> str:
    # <title>
    text = re.sub(
        r"<title>.*?</title>",
        f"<title>{xml_text(new_h1)} | Source of Truth</title>",
        text,
        count=1,
    )
    # og:title
    text = re.sub(
        r'(<meta property="og:title" content=")[^"]*(">)',
        lambda m: f"{m.group(1)}{xml_text(new_h1)} | Stefano Costa{m.group(2)}",
        text,
        count=1,
    )
    # JSON-LD headline (JSON string escapes)
    def _headline(m: re.Match) -> str:
        esc = new_h1.replace("\\", "\\\\").replace('"', '\\"')
        return f"{m.group(1)}{esc}{m.group(2)}"

    text = re.sub(r'("headline":\s*")[^"]*(")', _headline, text, count=1)
    return text


def build_new_h1(h1: str, subtitle: str | None) -> str:
    h1_plain = strip_tags(h1).strip()
    if not subtitle:
        return h1_plain
    sub_plain = strip_tags(subtitle).strip()
    if not sub_plain:
        return h1_plain
    # Preserve inline HTML in subtitle (e.g. <i>) but title text needs plain for <title>
    if "<" in subtitle:
        return f"{h1_plain}: {subtitle}"
    return f"{h1_plain}: {sub_plain}"


def rebuild_header(text: str) -> tuple[str, str, str | None, str]:
    """Reorder body header: h1, center, tldr, commented-toc. Returns
    (text, new_h1_display, es_body, extra_id)."""
    # Capture pieces
    h1_m = re.search(r"[ \t]*<h1[^>]*>(.*?)</h1>\s*\n", text, re.S)
    if not h1_m:
        raise ValueError("no h1")
    h1_inner = h1_m.group(1).strip()
    h1_start, h1_end = h1_m.start(), h1_m.end()

    text_wo_h1 = text[:h1_start] + text[h1_end:]
    text_wo_h1, subtitle, extra_id = extract_h2_subtitle(text_wo_h1)
    text_wo_h1, es_body = extract_h3_subtitle(text_wo_h1)
    text_wo_h1, center_info = extract_center(text_wo_h1)

    # Remove active section.toc (keep nothing — commented details goes after tldr)
    text_wo_h1 = re.sub(
        r"[ \t]*<section class=\"toc\">.*?</section>\s*\n",
        "",
        text_wo_h1,
        flags=re.S,
    )

    new_h1_display = build_new_h1(h1_inner, subtitle)
    # For <h1> keep HTML subtitle if any
    if subtitle and "<" in subtitle:
        h1_html = f"{h1_inner}: {subtitle}"
    elif subtitle:
        h1_html = f"{h1_inner}: {subtitle}"
    else:
        h1_html = h1_inner

    date_raw = center_info.get("divs", [""])[0] if center_info.get("divs") else ""
    length_raw = center_info.get("divs", ["", ""])[1] if len(center_info.get("divs", [])) > 1 else ""
    # If only one div somehow, date only
    if len(center_info.get("divs", [])) == 1:
        length_raw = ""
    indent = center_info.get("indent", "        ")

    center_block = build_center(indent, date_raw, length_raw, es_body)

    # Insert h1 + center right after <div class="bottom_space_big">
    anchor = re.search(r'(<div class="bottom_space_big">\s*\n)', text_wo_h1)
    if not anchor:
        raise ValueError("no bottom_space_big anchor")
    header = f"{indent}<h1>{h1_html}</h1>\n\n{center_block}\n"

    # Remove old leftover blank area before tldr — insert header at anchor
    text2 = text_wo_h1[: anchor.end()] + header + text_wo_h1[anchor.end():]

    # After </section> of tldr, insert commented TOC (once)
    if "toc-details" not in text2:
        tldr_end = re.search(
            r'(<section class="tldr">.*?</section>\s*\n)',
            text2,
            re.S,
        )
        if tldr_end:
            insert_at = tldr_end.end()
            text2 = text2[:insert_at] + "\n" + TOC_COMMENTED + text2[insert_at:]
        else:
            # no tldr? put before first content h2
            m2 = re.search(r'([ \t]*<h2 id=)', text2)
            if m2:
                text2 = text2[: m2.start()] + TOC_COMMENTED + text2[m2.start():]

    plain_h1 = strip_tags(new_h1_display).strip()
    # If display has HTML, use plain for title checks
    if subtitle:
        plain = f"{strip_tags(h1_inner).strip()}: {strip_tags(subtitle).strip()}"
    else:
        plain = strip_tags(h1_inner).strip()
    return text2, plain, es_body, extra_id


def migrate(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    text, plain_h1, _es, _eid = rebuild_header(text)
    text = strip_h2_square(text)
    text = rewrite_h3_tree(text)
    text = remove_trailing_hr(text)
    text = remove_block_stray_br(text)
    text = comment_footer(text)
    text = update_head_titles(text, plain_h1)
    # Normalize: ensure footer comment exists at end if we replaced active one
    return text


def main() -> int:
    files = sorted(
        p for p in BLOG.glob("*.html") if p.name not in SKIP
    )
    if not files:
        print("no files", file=sys.stderr)
        return 1
    for p in files:
        before = p.read_text(encoding="utf-8")
        try:
            after = migrate(p)
        except Exception as e:
            print(f"FAIL {p.name}: {e}", file=sys.stderr)
            return 1
        if after == before:
            print(f"SKIP {p.name} (unchanged)")
            continue
        p.write_text(after, encoding="utf-8")
        print(f"OK   {p.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
