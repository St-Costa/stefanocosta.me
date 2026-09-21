#!/usr/bin/env python3
"""
Controlla che il sito rispetti le regole descritte in CLAUDE.md.

Non è un linter generico: verifica le invarianti che questo progetto si è dato e
che, se violate, rompono qualcosa di concreto (rendering, feed RSS, anteprime
social, accessibilità, performance). Ogni controllo nasce da un bug realmente
capitato.

Uso:  python3 scripts/check_site.py        (dalla root del repo)
Exit code 0 se tutto ok, 1 se c'è almeno un errore.
Gli avvisi non bloccano il commit: segnalano debito noto (immagini legacy,
file pesanti preesistenti). Una pagina NUOVA o modificata non deve aggiungerne:
la skill .claude/skills/pre-commit-review/ tratta gli avvisi sulle righe
cambiate come bloccanti, insieme ai controlli qualitativi che richiedono
giudizio (qualità di description/alt, contrasto, mobile, link esterni).
"""
import glob
import os
import re
import sys
import urllib.parse
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
            err(rel, f"meta description di {len(desc.group(1))} caratteri (max 160)")

    title = re.search(r"<title>(.*?)</title>", html, re.S)
    if not title or not title.group(1).strip():
        err(rel, "manca <title> non vuoto")

    if 'name="viewport"' not in html:
        err(rel, 'manca <meta name="viewport"> (mobile responsiveness)')

    if 'rel="icon"' not in html:
        err(rel, 'manca <link rel="icon"> (favicon esplicita, non solo fallback JS)')

    ogimg = re.search(r'property="og:image" content="([^"]+)"', html)
    if ogimg:
        url = ogimg.group(1)
        if url.startswith("https://stefanocosta.me/"):
            local = urllib.parse.unquote(url.replace("https://stefanocosta.me/", ""))
            if not os.path.exists(os.path.join(ROOT, local)):
                err(rel, f"og:image punta a un file inesistente: {url}")
        else:
            err(rel, f"og:image deve stare su stefanocosta.me (niente terze parti): {url}")

    # Niente http:// in chiaro: il sito è servito in HTTPS (GitHub Pages + CNAME).
    # Gli xmlns dei namespace SVG (xmlns="http://...") non usano href/src e
    # restano fuori da questo controllo di proposito.
    for m in re.finditer(r'(?:href|src)\s*=\s*"http://[^"]+"', html):
        err(rel, f"link http:// non cifrato (usare https): {m.group(0)[:70]}")
    for m in re.finditer(r"url\(\s*http://[^)]+\)", html):
        err(rel, f"url() http:// non cifrata (usare https): {m.group(0)[:70]}")

    # Il sito non deve contattare terze parti: niente CDN, embed o immagini hotlinked.
    # I <a href> verso l'esterno vanno benissimo — sono link, non richieste.
    for m in re.finditer(r'<(img|script|link|source|iframe)[^>]+(?:src|href)="(https?://[^"]+)"', html):
        err(rel, f"richiesta a terze parti in <{m.group(1)}>: {m.group(2)[:70]}")

    for m in re.finditer(r"<button(?![^>]*aria-label)[^>]*>(.*?)</button>", html, re.S):
        if "<svg" in m.group(1) or not m.group(1).strip():
            err(rel, "<button> con sola icona senza aria-label")

    for m in re.finditer(r"<img\b[^>]*>", html):
        tag = m.group(0)
        if "alt" not in tag:
            err(rel, f"<img> senza alt (decorativa → alt=\"\"): {tag[:80]}")
        src = re.search(r'src="([^"]+)"', tag)
        if src and not src.group(1).startswith(("http", "data:")):
            # Gli SVG scalano senza sgranare: width/height servono alle raster.
            if not src.group(1).lower().endswith(".svg"):
                if "width" not in tag or "height" not in tag:
                    err(rel, f"<img> raster senza width/height reali (layout shift): {tag[:80]}")

    if re.search(r"document\.cookie", html):
        if not re.search(r"consent|cookie-banner|cookie_banner", html, re.I):
            err(rel, "usa document.cookie senza banner di consenso")

    # Il sito oggi non ha form: questi controlli scattano solo se qualcuno
    # ne aggiunge uno. Allora servono validazione e anti-spam.
    if re.search(r"<form\b", html):
        if "<label" not in html:
            err(rel, "<form> senza <label>: i campi non sono accessibili")
        for f in re.findall(r"<(?:input|textarea|select)\b[^>]*>", html):
            if re.search(r'type="(hidden|submit|button)"', f):
                continue
            if "name=" not in f:
                err(rel, f"campo form senza name (non inviabile): {f[:60]}")
        if not re.search(r"required|type=\"email\"|pattern=|minlength|checkValidity|validate", html):
            err(rel, "<form> senza validazione (required/type/pattern o JS)")
        form_tag = re.search(r"<form\b[^>]*>", html).group(0)
        if re.search(r'method="post"|action="https?://', form_tag, re.I):
            if not re.search(r"honeypot|captcha|turnstile|akismet", html, re.I):
                err(rel, "<form> che invia dati senza anti-spam (honeypot/captcha/Turnstile)")

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
    """Un post senza datePublished resta fuori dal feed RSS, in silenzio.

    Eccezione: un post con il marcatore <!-- unlisted-post --> è volutamente
    senza datePublished (vedi CLAUDE.md "Post nascosti (unlisted)")."""
    for path in glob.glob(os.path.join(ROOT, "blogPosts", "*.html")):
        name = os.path.basename(path)
        if name.startswith("_"):
            continue
        html = open(path, encoding="utf-8").read()
        rel = os.path.join("blogPosts", name)
        if '"datePublished"' not in html and "unlisted-post" not in html:
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


SECRET_PATTERNS = [
    (r"AKIA[0-9A-Z]{16}", "possibile AWS access key"),
    (r"ghp_[A-Za-z0-9]{36,}|gho_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{20,}",
     "possibile GitHub token"),
    (r"xox[baprs]-[A-Za-z0-9-]{10,}", "possibile Slack token"),
    (r"-----BEGIN (?:RSA )?PRIVATE KEY-----", "chiave privata nel repo"),
    (r"sk-[A-Za-z0-9]{20,}", "possibile API key (sk-...)"),
    (r"(?i)(api[_-]?key|api[_-]?secret|secret[_-]?key|access[_-]?token|auth[_-]?token)"
     r"\s*[:=]\s*['\"][^'\"]{12,}['\"]", "possibile secret assegnato in chiaro"),
]
SECRET_EXTS = {".html", ".css", ".js", ".py", ".xml", ".json",
               ".yml", ".yaml", ".md", ".txt", ".svg"}


def check_secrets():
    """Nessuna chiave/token/password deve finire nel repo pubblico.

    Mandare un secret a una LLM per "controllarlo" sarebbe peggio: per questo
    la ricerca è una regex deterministica, mai una review esterna."""
    for path in glob.glob(os.path.join(ROOT, "**", "*"), recursive=True):
        if not os.path.isfile(path) or ".git/" in path:
            continue
        if os.path.splitext(path)[1].lower() not in SECRET_EXTS:
            continue
        rel = os.path.relpath(path, ROOT)
        try:
            text = open(path, encoding="utf-8").read()
        except (UnicodeDecodeError, OSError):
            continue
        for pat, label in SECRET_PATTERNS:
            if re.search(pat, text):
                err(rel, f"{label} — rimuoverlo prima di committare")
                break


def check_js_css():
    """CSS/JS locali: niente http:// e niente cookie senza consenso."""
    for path in glob.glob(os.path.join(ROOT, "style", "*.css")) + \
                glob.glob(os.path.join(ROOT, "javascript", "*.js")):
        rel = os.path.relpath(path, ROOT)
        text = open(path, encoding="utf-8").read()
        if "http://" in text:
            err(rel, "http:// in chiaro: usare https")
        if path.endswith(".js") and re.search(r"document\.cookie|localStorage", text):
            if not re.search(r"consent|cookie-banner|cookie_banner", text, re.I):
                err(rel, "cookie/storage senza banner di consenso")


def check_sitemap_robots():
    """Ogni pagina deve stare in sitemap.xml; robots.txt deve restare valido."""
    sm = os.path.join(ROOT, "sitemap.xml")
    if not os.path.exists(sm):
        err("sitemap.xml", "file mancante")
        return
    locs = re.findall(r"<loc>(.*?)</loc>", open(sm, encoding="utf-8").read())

    def loc_to_file(loc):
        p = urllib.parse.unquote(loc.replace("https://stefanocosta.me/", ""))
        return "index.html" if p in ("", "/") else p

    for loc in locs:
        f = loc_to_file(loc)
        if not os.path.exists(os.path.join(ROOT, f)):
            err("sitemap.xml", f"entry senza file: {loc}")
    mapped = {loc_to_file(l) for l in locs}
    for path in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True):
        rel = os.path.relpath(path, ROOT)
        name = os.path.basename(path)
        if name in ("404.html",) or name.startswith("_"):
            continue  # 404 e template: non vanno indicizzati
        if rel not in mapped:
            err(rel, "pagina non in sitemap.xml")

    rb = os.path.join(ROOT, "robots.txt")
    if not os.path.exists(rb):
        err("robots.txt", "file mancante")
        return
    robots = open(rb, encoding="utf-8").read()
    if "Sitemap:" not in robots:
        err("robots.txt", "manca la riga Sitemap:")
    for must in ("/document/", "_template.html", "/.claude/"):
        if must not in robots:
            err("robots.txt", f"manca il Disallow per {must}")


def check_image_assets():
    """Formato e peso delle immagini: avvisi (debito noto), non errori.

    Le immagini nuove devono essere WebP leggere (vedi CLAUDE.md): la skill
    pre-commit-review tratta questi avvisi come bloccanti sulle righe cambiate."""
    legacy, big = [], []
    for path in glob.glob(os.path.join(ROOT, "img", "**", "*"), recursive=True):
        if not os.path.isfile(path):
            continue
        ext = os.path.splitext(path)[1].lower()
        if ext not in (".jpg", ".jpeg", ".png", ".webp"):
            continue
        rel = os.path.relpath(path, ROOT)
        if ext in (".jpg", ".jpeg", ".png") and os.path.basename(path) != "preview_image.jpg":
            legacy.append(rel)
        if os.path.getsize(path) > 1024 * 1024 and os.path.basename(path) != "preview_image.jpg":
            big.append(rel)
    if legacy:
        warn("img/", f"{len(legacy)} file legacy JPG/PNG (nuove immagini → WebP): "
             + ", ".join(sorted(legacy)[:5]) + ("…" if len(legacy) > 5 else ""))
    if big:
        warn("img/", f"{len(big)} file >1MB (valutare compressione): " + ", ".join(sorted(big)))


def check_page_weight():
    """Proxy della page-load-speed: immagini locali referenziate oltre 2MB."""
    for path in glob.glob(os.path.join(ROOT, "**", "*.html"), recursive=True):
        rel = os.path.relpath(path, ROOT)
        html = open(path, encoding="utf-8").read()
        base = os.path.dirname(path)
        total = 0
        for m in re.finditer(r'(?:src|href)="((?!https?://|#|mailto:|data:)[^"]+)"', html):
            target = m.group(1).split("#")[0].split("?")[0]
            if not target:
                continue
            full = os.path.normpath(os.path.join(base, target))
            if os.path.isfile(full) and full.startswith(os.path.join(ROOT, "img")):
                total += os.path.getsize(full)
        if total > 2 * 1024 * 1024:
            warn(rel, f"pagina pesante: {total // 1024}KB di immagini locali (rallenta il load)")


def main():
    os.chdir(ROOT)
    pages = sorted(glob.glob("**/*.html", recursive=True))
    for path in pages:
        check_page(os.path.join(ROOT, path), open(path, encoding="utf-8").read())
    check_posts()
    check_inline_css()
    check_orphan_css()
    check_secrets()
    check_js_css()
    check_sitemap_robots()
    check_image_assets()
    check_page_weight()

    for w in warnings:
        print(f"  avviso  {w}")
    for e in errors:
        print(f"  ERRORE  {e}")

    print(f"\n{len(pages)} pagine controllate — "
          f"{len(errors)} errori, {len(warnings)} avvisi")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
