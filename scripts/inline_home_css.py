#!/usr/bin/env python3
"""
Inlina base.css dentro index.html, fra i marcatori INLINE-CSS.

Perché solo la homepage: è la pagina del primo accesso, quella con la cache
vuota, dove il round-trip in più per il CSS costa di più — ed è anche la più
piccola (1.6 KB gzip), quindi i ~3 KB di CSS pesano poco in confronto al giro
di rete che eliminano. Le altre 28 pagine tengono il <link>: chi arriva lì ha
quasi sempre già base.css in cache, e duplicare il CSS ovunque lo renderebbe
non cacheabile fra pagine.

L'HTML resta la fonte di verità solo per il markup: il CSS vive in
style/base.css e questo script rigenera la copia inline, così le due non
divergono. Rilanciarlo dopo ogni modifica a base.css — il pre-commit hook
verifica che siano allineati.

Uso:  python3 scripts/inline_home_css.py [--check]
      --check  esce con 1 se l'inline è disallineato, senza riscrivere
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "index.html")
CSS = os.path.join(ROOT, "style", "base.css")

BEGIN = "<!-- INLINE-CSS:begin — generato da scripts/inline_home_css.py, non modificare a mano -->"
END = "<!-- INLINE-CSS:end -->"


def build_block(css_text):
    # url() dentro base.css sono root-relative, quindi restano validi una volta
    # inlinati: è la ragione per cui l'inline è possibile senza riscritture.
    return f"{BEGIN}\n    <style>\n{css_text.rstrip()}\n    </style>\n    {END}"


def main():
    check_only = "--check" in sys.argv
    html = open(INDEX, encoding="utf-8").read()
    css_text = open(CSS, encoding="utf-8").read()
    block = build_block(css_text)

    pattern = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END), re.S)

    if pattern.search(html):
        new = pattern.sub(lambda _: block, html)
    else:
        link = re.search(r'[ \t]*<link rel="stylesheet" href="\./style/base\.css">\n', html)
        if not link:
            print("index.html: non trovo né il blocco inline né il <link> a base.css",
                  file=sys.stderr)
            return 1
        new = html[:link.start()] + "    " + block + "\n" + html[link.end():]

    if new == html:
        if check_only:
            print("index.html: CSS inline allineato con style/base.css")
        return 0

    if check_only:
        print("index.html: il CSS inline NON è allineato con style/base.css.\n"
              "            Esegui: python3 scripts/inline_home_css.py", file=sys.stderr)
        return 1

    open(INDEX, "w", encoding="utf-8").write(new)
    print(f"index.html: CSS inline aggiornato ({len(css_text)} byte da style/base.css)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
