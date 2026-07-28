#!/usr/bin/env python3
"""
Rigenera interamente mainPages/blogFeed.xml a partire dai post in blogPosts/.

Struttura di ogni <description> (HTML in entità, come vuole RSS):
  <strong>Titolo</strong>
  <em>Sottotitolo</em>
  Epistemic status: ...
  <data> - <lunghezza> - <tempo lettura>
  <strong>Headers of the post:</strong> <ul><li>...</li></ul>

I post inclusi sono solo quelli con "datePublished" nel JSON-LD
(esclude automaticamente _template.html e ogni bozza priva di data).
Ordinamento: data decrescente (più recente in cima).

Uso:  python3 scripts/gen_feed.py        (dalla root del repo)
"""
import re, html, glob, os
from html.parser import HTMLParser
from datetime import datetime
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG_DIR = os.path.join(ROOT, "blogPosts")
FEED = os.path.join(ROOT, "mainPages", "blogFeed.xml")
# Dominio del sito. Sovrascrivibile con la variabile d'ambiente SITE_BASE_URL,
# es. `SITE_BASE_URL="https://esempio.com" python3 scripts/gen_feed.py`.
BASE_URL = os.environ.get("SITE_BASE_URL", "https://stefanocosta.me").rstrip("/")

CHANNEL_HEADER = f"""<rss version="2.0">
<channel>
  <title>Source of Truth</title>
  <link>{BASE_URL}/mainPages/Blog_pages.html</link>
  <description>Source of Truth — Stefano Costa's blog</description>
  <language>en-us</language>

  <image>
    <url>{BASE_URL}/blogPosts/RSS_logo.png</url>
    <title>Source of Truth</title>
    <link>{BASE_URL}/mainPages/Blog_pages.html</link>
  </image>
"""


class Extractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.buf = []
        self.capture = None
        self.h1 = None
        self.subtitle = None
        self.epistemic = None
        self.center_divs = []
        self.headers = []
        self._in_center = 0
        self._center_div_depth = None
        self._h2_id_depth = None

    def _cls(self, attrs):
        d = dict(attrs)
        return d.get("class", ""), d

    def handle_starttag(self, tag, attrs):
        cls, d = self._cls(attrs)
        self.stack.append((tag, cls, d))
        if tag == "h1" and self.h1 is None:
            self.capture = "h1"; self.buf = []
        elif tag == "h2" and "subtitle" in cls and self.subtitle is None:
            self.capture = "subtitle"; self.buf = []
        elif tag == "h3" and "subtitle" in cls and self.epistemic is None:
            self.capture = "epistemic"; self.buf = []
        elif tag == "div" and "center" in cls:
            self._in_center += 1
        elif tag == "div" and self._in_center and self._center_div_depth is None:
            self._center_div_depth = len(self.stack)
            self.capture = "centerdiv"; self.buf = []
        elif tag == "h2" and "id" in d and "subtitle" not in cls:
            self._h2_id_depth = len(self.stack)
            self.capture = "header"; self.buf = []

    def handle_endtag(self, tag):
        depth = len(self.stack)
        if self.capture == "h1" and tag == "h1":
            self.h1 = self._flush(); self.capture = None
        elif self.capture == "subtitle" and tag == "h2":
            self.subtitle = self._flush(); self.capture = None
        elif self.capture == "epistemic" and tag == "h3":
            self.epistemic = self._flush(); self.capture = None
        elif self.capture == "centerdiv" and self._center_div_depth == depth:
            self.center_divs.append(self._flush()); self.capture = None
            self._center_div_depth = None
        elif self.capture == "header" and self._h2_id_depth == depth:
            self.headers.append(self._flush()); self.capture = None
            self._h2_id_depth = None
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                popped = self.stack.pop(i)
                if popped[0] == "div" and "center" in popped[1] and self._in_center:
                    self._in_center -= 1
                break

    def handle_data(self, data):
        if self.capture:
            self.buf.append(data)

    def _flush(self):
        return re.sub(r"\s+", " ", "".join(self.buf)).strip()


def clean_header(t):
    t = t.replace("■", "")
    t = re.sub(r"\[\*\]", "", t)
    return re.sub(r"\s+", " ", t).strip()


def esc(s):
    return html.escape(s, quote=False)


def parse_post(path):
    with open(path, encoding="utf-8") as f:
        content = f.read()
    m = re.search(r'"datePublished"\s*:\s*"([0-9]{4}-[0-9]{2}-[0-9]{2})"', content)
    if not m:
        return None  # non è un post pubblicato (template/test)
    date_iso = m.group(1)
    p = Extractor()
    p.feed(content)
    return {
        "date_iso": date_iso,
        "filename": os.path.basename(path),
        "title": p.h1 or "",
        "subtitle": p.subtitle or "",
        "epistemic": p.epistemic or "",
        "date_human": p.center_divs[0] if len(p.center_divs) > 0 else "",
        "length_read": p.center_divs[1] if len(p.center_divs) > 1 else "",
        "headers": [clean_header(h) for h in p.headers if clean_header(h)],
    }


def build_description(d):
    parts = [f"&lt;strong&gt;{esc(d['title'])}&lt;/strong&gt;"]
    if d["subtitle"]:
        parts.append(f"&lt;em&gt;{esc(d['subtitle'])}&lt;/em&gt;")
    if d["epistemic"]:
        parts.append(esc(d["epistemic"]))
    meta = " - ".join(x for x in [d["date_human"], d["length_read"]] if x)
    if meta:
        parts.append(esc(meta))
    if d["headers"]:
        hs = "".join(f"&lt;li&gt;{esc(h)}&lt;/li&gt;" for h in d["headers"])
        parts.append("&lt;strong&gt;Headers of the post:&lt;/strong&gt;&lt;ul&gt;" + hs + "&lt;/ul&gt;")
    return "".join(f"&lt;p&gt;{p}&lt;/p&gt;" for p in parts)


def build_item(d):
    url = f"{BASE_URL}/blogPosts/{quote(d['filename'])}"
    pub = datetime.strptime(d["date_iso"], "%Y-%m-%d").strftime("%a, %d %b %Y 12:00:00 GMT")
    return f"""
  <item>
    <title>{esc(d['title'])}</title>
    <link>{url}</link>
    <description>{build_description(d)}</description>
    <pubDate>{pub}</pubDate>
    <guid>{url}</guid>
  </item>
"""


def main():
    posts = []
    for path in glob.glob(os.path.join(BLOG_DIR, "*.html")):
        d = parse_post(path)
        if d:
            posts.append(d)
    posts.sort(key=lambda d: d["date_iso"], reverse=True)

    feed = CHANNEL_HEADER + "".join(build_item(d) for d in posts) + "\n</channel>\n</rss>\n"
    with open(FEED, "w", encoding="utf-8") as f:
        f.write(feed)
    print(f"Feed rigenerato: {len(posts)} post -> {os.path.relpath(FEED, ROOT)}")


if __name__ == "__main__":
    main()
