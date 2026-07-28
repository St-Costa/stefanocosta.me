# stefanocosta.me — istruzioni per Claude

Sito personale statico (HTML/CSS/JS puro), ospitato su GitHub Pages. Nessun build system.

> **Questo file è codice, non appunti.** Se una modifica cambia una regola descritta qui
> (struttura del `<head>`, CSS disponibili, convenzioni su immagini o accessibilità),
> aggiornare questo file **nello stesso commit**. Una pagina nuova viene scritta seguendo
> queste istruzioni: se sono obsolete, reintroducono i bug appena corretti.
>
> Vale anche per `blogPosts/_template.html` e `.claude/skills/`: sono la stessa
> documentazione in forma eseguibile. Cambiando l'una, verificare le altre.

## Controlli automatici

`scripts/check_site.py` verifica le regole di questo file su tutte le pagine: `<main>`,
OG tag statici, `defer`, preload dei font, `aria-label` sui bottoni-icona, riferimenti
locali, `datePublished` nei post, CSS orfani.

**Gira da solo a ogni `git commit`** (hook in `scripts/githooks/pre-commit`): se trova un
errore, il commit viene annullato. Non serve eseguirlo a mano.

```bash
python3 scripts/check_site.py     # solo se lo vuoi lanciare prima di committare
git commit --no-verify            # scavalca l'hook, per casi eccezionali
```

Su un clone nuovo l'hook va attivato una volta (Git non clona gli hook):
```bash
git config core.hooksPath scripts/githooks
```

Le regole che lo script **non** può controllare (qualità della description, alt text
sensati, scelta della `priority` in sitemap) restano responsabilità di chi scrive.

---

## Checklist per ogni nuova pagina HTML

### `<head>` — ordine obbligatorio

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Descrizione specifica di questa pagina (max 160 caratteri).">
    <title>Titolo pagina | Stefano Costa</title>
    <link rel="preload" href="[PATH]/style/fonts/JetBrainsMono-Regular.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="preload" href="[PATH]/style/fonts/JetBrainsMono-Bold.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="stylesheet" href="[PATH]/style/base.css">
    <meta property="og:title" content="Titolo pagina | Stefano Costa">
    <meta property="og:description" content="Stessa stringa della meta description.">
    <meta property="og:image" content="https://stefanocosta.me/img/preview_image.jpg">
    <meta property="og:url" content="https://stefanocosta.me/PERCORSO.html">
    <meta property="og:type" content="website">
    <link rel="icon" type="image/svg+xml" href="[PATH]/img/icon/favicon.svg">
    <script src="[PATH]/javascript/commonHeader.js" defer></script>

    <!-- CSS aggiuntivi specifici per questa pagina -->
    <link rel="stylesheet" href="[PATH]/style/blog.css">  <!-- solo se blog post -->
</head>
```

Tre regole dietro a quest'ordine:

1. **`base.css` linkato direttamente**, così il browser lo scarica mentre parsa l'HTML.
2. **OG tag e favicon scritti in chiaro nell'HTML**, non iniettati da JS: i crawler social
   (LinkedIn, WhatsApp, Slack) spesso non eseguono JavaScript, e un OG tag aggiunto a runtime
   per loro non esiste.
3. **`commonHeader.js` con `defer`**: non serve al primo paint, quindi non deve bloccarlo.
   Resta come rete di sicurezza — aggiunge favicon, `base.css` e OG tag solo se mancano —
   ma una pagina scritta bene non gli fa fare nulla.

Si preloadano **due** font: gli heading ereditano il bold di default del browser, quindi
il Bold è sul percorso critico quanto il Regular.

Il `<body>` deve racchiudere il contenuto in `<main>` (landmark di accessibilità),
chiuso **prima** del footer:
```html
<body>
    <main>
        ...contenuto...
    </main>
    <script src="[PATH]/javascript/footer.js"></script>
</body>
```

`[PATH]` dipende dalla posizione della pagina:
- Root (`/`): `./`
- Sottocartelle (`/mainPages/`, `/blogPosts/`, `/subpages/`): `../`

**Non** aggiungere reset, tipografia, footer o media query: sono già in `base.css`.

### `commonHeader.js` è un fallback, non una dipendenza
Aggiunge favicon, `base.css` e OG tag **solo se assenti** dall'HTML. Su una pagina scritta
seguendo il template qui sopra non fa nulla: serve a non lasciare una pagina senza stile o
senza anteprima se qualcuno dimentica un tag. Non spostarci dentro logica necessaria al
rendering, e non togliergli il `defer`.

Il font JetBrains Mono è **self-hosted** in `style/fonts/` e dichiarato con `@font-face`
dentro `base.css`. Non aggiungere link a Google Fonts o ad altri CDN: il sito non deve
fare **nessuna** richiesta a terze parti.

Gli `url()` dentro `base.css` sono **assoluti dalla root** (`/style/fonts/…`, `/img/icon/…`),
non relativi: restano validi da qualsiasi cartella. Mantenere questa forma.

### CSS disponibili (da aggiungere manualmente solo se servono)
| File | Quando usarlo |
|------|---------------|
| `style/blog.css` | Blog post con TOC fisso a sinistra |
| `style/gallery.css` | Pagine con slideshow gallery |
| `style/about_me_cards.css` | Solo `aboutme.html` |

`base.css` contiene già reset, font, token, **componenti** (immagini, icone, liste, bottoni,
tabelle, layout a 2 colonne) e media query, in quest'ordine. Molte pagine caricano solo lui.

⚠️ Aggiungendo regole a `base.css`, inserirle **prima** della sezione `── Responsive ──`:
i breakpoint sovrascrivono di proposito diverse regole dei componenti.

### Icone
Le icone sono **SVG inline** (path di Font Awesome Free, CC BY 4.0) con classe `.fa_icon`,
non un webfont. Per aggiungerne una, copiare un `<svg class="fa_icon">` esistente da
`subpages/Thesis.html`. Il `fill="currentColor"` fa ereditare il colore da `.fa_icon`.

### `<body>` — footer

Ogni pagina deve chiudersi con uno di questi:
```html
<script src="[PATH]/javascript/footer.js"></script>   <!-- pagine normali -->
```
Oppure footer manuale se il layout lo richiede (vedi `index.html`).

---

## Blog post — checklist aggiuntiva

### `<head>` completo
```html
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="...">
    <title>Titolo post | Source of Truth</title>
    <link rel="preload" href="../style/fonts/JetBrainsMono-Regular.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="preload" href="../style/fonts/JetBrainsMono-Bold.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="stylesheet" href="../style/base.css">
    <meta property="og:title" content="Titolo post | Stefano Costa">
    <meta property="og:description" content="Stessa stringa della meta description.">
    <meta property="og:image" content="https://stefanocosta.me/img/preview_image.jpg">
    <meta property="og:url" content="https://stefanocosta.me/blogPosts/Nome%20File.html">
    <meta property="og:type" content="article">
    <link rel="icon" type="image/svg+xml" href="../img/icon/favicon.svg">
    <script src="../javascript/commonHeader.js" defer></script>
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "BlogPosting",
      "headline": "Titolo post",
      "datePublished": "YYYY-MM-DD",
      "author": {"@type": "Person", "name": "Stefano Costa", "url": "https://stefanocosta.me/"},
      "url": "https://stefanocosta.me/blogPosts/Nome%20File.html",
      "description": "Stessa stringa della meta description."
    }
    </script>
    <link rel="stylesheet" href="../style/blog.css">
    <!-- se ha gallery: -->
    <link rel="stylesheet" href="../style/gallery.css">
</head>
```

### TOC (generato automaticamente)
```html
<script src="../javascript/toc.js"></script>   <!-- nel <head> -->

<section class="toc">                          <!-- nel <body>, dopo il blocco h1/subtitle/data -->
    <div class="box-title"><h4>TOC</h4></div>
</section>
```
`toc.js` riempie il `.toc` leggendo gli `<h2 id="...">` della pagina: non scrivere le voci
a mano. Il `.box-title` è il titolo flottante sul bordo (vedi note tecniche in fondo).

### Gallery (se presente)
```html
<link rel="stylesheet" href="../style/gallery.css">  <!-- in <head> -->
<script src="../javascript/gallery.js"></script>       <!-- in fondo a <body> -->
```

### Aggiungere il post a `mainPages/Blog_pages.html`
```html
<li><h2><a href="../blogPosts/Nome File.html">Titolo [YYYY-MM-DD]</a></h2></li>
```
Inserire **in cima** alla lista (post più recente prima).

### Rigenerare il feed RSS `mainPages/blogFeed.xml`
**Non** modificare il feed a mano. Dopo aver creato/modificato un post, rigenerarlo con:
```bash
python3 scripts/gen_feed.py
```
Lo script (stdlib only, nessuna dipendenza) ricostruisce l'intero feed leggendo i post in `blogPosts/`. Include solo i post con `datePublished` nel JSON-LD (esclude quindi `_template.html` e le bozze senza data), li ordina per data decrescente, e per ogni post genera una `<description>` con: titolo, sottotitolo, epistemic status, `data - lunghezza - tempo lettura`, ed elenco degli header di sezione.

Perché funzioni, il post deve avere: JSON-LD con `datePublished`, `<h1>` (titolo), `<h2 class="subtitle">` (sottotitolo), `<h3 class="subtitle">` (epistemic), i due `<div>` dentro `.center` (data; poi `N words - M min read`), e gli header di sezione come `<h2 id="...">`.

### Aggiungere il post a `sitemap.xml`
```xml
<url>
    <loc>https://stefanocosta.me/blogPosts/Nome%20File.html</loc>
    <changefreq>yearly</changefreq>
    <priority>0.7</priority>
</url>
```

---

## Immagini — regole

### Formato
- **Usare sempre WebP** per immagini nuove. Convertire con ImageMagick:
  ```bash
  convert originale.jpg -quality 80 originale.webp
  # batch su tutte le immagini non ancora convertite:
  find img/ \( -name "*.jpg" -o -name "*.png" \) | while read f; do
      [ -f "${f%.*}.webp" ] || convert "$f" -quality 80 "${f%.*}.webp"
  done
  ```
- Eccezione: `preview_image.jpg` resta JPG per compatibilità con crawler OG.
- Gli SVG restano SVG (già vettoriali): non convertirli.

### Lazy loading e dimensioni
- `loading="lazy"` va su tutte le `<img>` **sotto** la piega. **Mai** su quelle above the fold
  (es. icone social in `index.html`): ritarderebbe proprio le immagini già in vista.
- Ogni `<img>` deve avere `width` e `height` con le dimensioni **reali** del file: danno al
  browser l'aspect ratio prima del download ed evitano il layout shift (CLS). Il CSS controlla
  la dimensione visibile, purché la regola includa `height: auto`.

### Alt text
- Immagini informative: testo descrittivo (`alt="Screenshot del progetto XYZ"`).
- Icone decorative con testo adiacente: `alt=""`.
- Copertine di libri/podcast: `alt="Titolo del libro/podcast"`.

### Posizione file
| Tipo | Cartella |
|------|----------|
| Screenshot progetti | `img/` |
| Foto per blog post | `img/blog/Nome Post/` |
| Icone UI | `img/icon/` |
| Anteprime poster | `img/poster preview/` |

---

## SEO — per ogni nuova pagina

- `<meta name="description">`: unica per pagina, max 160 caratteri.
- Aggiungere a `sitemap.xml` con `priority` appropriata:
  - Main pages: `0.8–0.9`
  - Blog posts: `0.7`
  - Subpages accademiche: `0.4–0.5`
- Per pagine importanti, aggiungere Schema.org JSON-LD adeguato.

---

## Accessibilità — regole

- `<button>` senza testo visibile → aggiungere `aria-label="..."`.
- Link con sola immagine → l'`<img>` deve avere `alt` descrittivo, oppure il `<a>` deve avere `aria-label`.
- Link social con sola icona → già gestiti in `index.html` con `aria-label` sull'`<a>`.
- Ogni pagina deve avere un `<main>` che racchiude il contenuto.
- Gli `<svg>` decorativi dentro un bottone vanno `aria-hidden="true"`: l'etichetta la dà l'`aria-label` del `<button>`.

---

## `robots.txt` — cosa è escluso

`/document/`, `_template.html`, `.claude/`.
Non aggiungere nuovi file sensibili o di staging senza aggiornarli.

---

## Struttura cartelle

```
/
├── index.html
├── 404.html
├── sitemap.xml
├── robots.txt
├── mainPages/        ← pagine principali
├── blogPosts/        ← post del blog
├── subpages/         ← approfondimenti accademici
├── style/            ← CSS (base.css + CSS specifici)
├── javascript/       ← commonHeader.js, footer.js, toc.js, gallery.js, about_me_cards.js
├── scripts/          ← gen_feed.py (feed RSS), check_site.py (controlli)
├── img/              ← immagini (sempre WebP)
└── document/         ← PDF accademici (non indicizzati)
```

---

## Note tecniche (decisioni già prese — non rifarle)

### Perché `blog.css` usa `body h2` invece di `h2`
Per vincere sulla cascade contro le regole a livello di elemento di `base.css`
(specificità `0,0,1`) senza ricorrere a `!important`: il prefisso `body`
porta la specificità a `0,0,2`, indipendentemente dall'ordine di caricamento.

### `components.css` è stato fuso dentro `base.css`
Erano due richieste render-blocking in serie su tutte e 29 le pagine. Le regole dei componenti
stanno ora in `base.css` fra le regole base e le media query. Non ricrearlo come file separato.

### `<fieldset>` decorativi → `<section>` + `.box-title`
Tutti i `<fieldset>` usati a scopo decorativo (`.briefAboutMe`, `.toc`, `.tldr`, `.callout`,
`.explanation_box`) sono stati sostituiti da `<section>`/`<div>`. L'effetto del `<legend>`
flottante sul bordo è replicato con `.box-title { position: absolute; top: 0; left: 50%;
transform: translate(-50%, -50%); }` su un contenitore `position: relative`. Il `.toc` usa un
`.toc-scroll` interno per gestire `overflow-y: auto` senza tagliare il `.box-title`.

### Link "Colophon" nel footer
`footer.js` rileva la cartella corrente e usa `../mainPages/colophon.html` per `subpages/` e
`blogPosts/`, `./colophon.html` per `mainPages/`. Non hardcodare il path.

### Anno di copyright
In `index.html` è aggiornato via JS (`#copyright-year`). Non scriverlo a mano.
