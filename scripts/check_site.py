#!/usr/bin/env python3
"""
Controlla che il sito rispetti le regole descritte in CLAUDE.md.

Non è un linter generico: verifica le invarianti che questo progetto si è dato e
che, se violate, rompono qualcosa di concreto (rendering, feed RSS, anteprime
social, accessibilità, performance). Ogni controllo nasce da un bug realmente
capitato.

Uso:  python3 scripts/check_site.py        (dalla root del repo)
Exit code 0 se tutto ok, 1 se c'è almeno un errore.
"""
import glob
import os
import re
import sys
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOID = {"meta", "link", "img", "br", "hr", "input", "source",
        "area", "base", "col", "embed", "param", "track", "wbr"}

errors = []
warnings = []


def err(page, msg):
    errors.append(f"{page}: {msg}")


def warn(page, msg):
    warnings.append(f"{page}: {msg}")


class Balance(HTMLParser):
    """Verifica che i tag siano bilanciati."""

    def __init__(self):
        super().__init__()
        self.stack = []
        self.problems = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.problems.append(f"</{tag}> di troppo")
        elif self.stack[-1] == tag:
            self.stack.pop()
        elif tag in self.stack:
            while self.stack and self.stack[-1] != tag:
                self.problems.append(f"<{self.stack.pop()}> non chiuso")
            if self.stack:
                self.stack.pop()
        else:
            self.problems.append(f"</{tag}> di troppo")

    def result(self):
        return self.problems + [f"<{t}> non chiuso" for t in self.stack]


def check_page(path, html):
    rel = os.path.relpath(path, ROOT)
    is_template = os.path.basename(path).startswith("_")

    parser = Balance()
    parser.feed(html)
    for p in parser.result():
        err(rel, p)

    if html.count("<main>") != 1 or html.count("</main>") != 1:
        err(rel, "manca il landmark <main> (accessibilità)")

    # La homepage inlina base.css invece di linkarlo (vedi inline_home_css.py);
    # ogni altra pagina deve linkarlo, altrimenti resta senza stile.
    if "INLINE-CSS:begin" not in html and "style/base.css" not in html:
        err(rel, "base.css né linkato né inlinato: la pagina resterebbe senza stile")

    if html.count('rel="preload"') != 2:
        err(rel, "servono 2 <link rel=preload> per i font (Regular + Bold)")

    if 'commonHeader.js" defer' not in html:
        err(rel, "commonHeader.js deve avere defer (non deve bloccare il render)")

    if "data-og-" in html:
        err(rel, "data-og-* è obsoleto: scrivere i <meta property=og:*> nell'HTML")

    for prop in ("og:title", "og:description", "og:image", "og:url", "og:type"):
        if f'property="{prop}"' not in html:
            err(rel, f"manca <meta property=\"{prop}\"> (i crawler non eseguono JS)")

    if not re.search(r'<meta name="description"', html):
        err(rel, "manca <meta name=\"description\">")
    else:
        desc = re.search(r'<meta name="description" content="([^"]*)"', html)
        if desc and len(desc.group(1)) > 160 and not is_template:
            warn(rel, f"meta description di {len(desc.group(1))} caratteri (max 160)")

    # Il sito non deve contattare terze parti: niente CDN, embed o immagini hotlinked.
    # I <a href> verso l'esterno vanno benissimo — sono link, non richieste.
    for m in re.finditer(r'<(img|script|link|source|iframe)[^>]+(?:src|href)="(https?://[^"]+)"', html):
        err(rel, f"richiesta a terze parti in <{m.group(1)}>: {m.group(2)[:70]}")

    for m in re.finditer(r"<button(?![^>]*aria-label)[^>]*>(.*?)</button>", html, re.S):
        if "<svg" in m.group(1) or not m.group(1).strip():
            err(rel, "<button> con sola icona senza aria-label")

    # riferimenti locali rotti
    base = os.path.dirname(path)
    for m in re.finditer(r'(?:href|src)="((?!https?:|#|mailto:|data:)[^"]+)"', html):
        target = m.group(1).split("#")[0].split("?")[0]
        if not target:
            continue
        root_dir = ROOT if target.startswith("/") else base
        full = os.path.normpath(os.path.join(root_dir, target.lstrip("/")))
        if not os.path.exists(full):
            err(rel, f"riferimento rotto: {m.group(1)}")


def check_posts():
    """Un post senza datePublished resta fuori dal feed RSS, in silenzio."""
    for path in glob.glob(os.path.join(ROOT, "blogPosts", "*.html")):
        name = os.path.basename(path)
        if name.startswith("_"):
            continue
        html = open(path, encoding="utf-8").read()
        rel = os.path.join("blogPosts", name)
        if '"datePublished"' not in html:
            err(rel, "post senza datePublished nel JSON-LD: non entrerà nel feed RSS")
        title = re.search(r"<title>(.*?)</title>", html, re.S)
        h1 = re.search(r"<h1>(.*?)</h1>", html, re.S)
        if title and h1:
            h1_text = re.sub(r"<[^>]+>", "", h1.group(1)).strip()
            if h1_text and h1_text.lower() not in title.group(1).lower():
                err(rel, f"<title> e <h1> divergono: {title.group(1)!r} vs {h1_text!r}")


def check_inline_css():
    """Il CSS inlinato nella homepage deve combaciare con style/base.css."""
    index = os.path.join(ROOT, "index.html")
    if not os.path.exists(index):
        return
    html = open(index, encoding="utf-8").read()
    if "INLINE-CSS:begin" not in html:
        return
    block = re.search(r"INLINE-CSS:begin.*?<style>\n(.*?)\n\s*</style>", html, re.S)
    if not block:
        err("index.html", "blocco INLINE-CSS malformato")
        return
    css = open(os.path.join(ROOT, "style", "base.css"), encoding="utf-8").read()
    if block.group(1).strip() != css.strip():
        err("index.html",
            "il CSS inline diverge da style/base.css — "
            "rigenera con: python3 scripts/inline_home_css.py")


def check_orphan_css():
    """Un CSS che nessuno carica è peso morto — ne avevamo nove."""
    pages = " ".join(open(p, encoding="utf-8").read()
                     for p in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True))
    for css in glob.glob(os.path.join(ROOT, "style", "*.css")):
        name = os.path.basename(css)
        if name == "base.css":
            continue
        if f"style/{name}" not in pages:
            warn(os.path.join("style", name), "non è caricato da nessuna pagina")


def main():
    os.chdir(ROOT)
    pages = sorted(glob.glob("**/*.html", recursive=True))
    for path in pages:
        check_page(os.path.join(ROOT, path), open(path, encoding="utf-8").read())
    check_posts()
    check_inline_css()
    check_orphan_css()

    for w in warnings:
        print(f"  avviso  {w}")
    for e in errors:
        print(f"  ERRORE  {e}")

    print(f"\n{len(pages)} pagine controllate — "
          f"{len(errors)} errori, {len(warnings)} avvisi")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
