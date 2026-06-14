# St-Costa.github.io — istruzioni per Claude

Sito personale statico (HTML/CSS/JS puro), ospitato su GitHub Pages. Nessun build system.

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
    <script src="[PATH]/javascript/commonHeader.js"></script>

    <!-- CSS aggiuntivi specifici per questa pagina -->
    <link rel="stylesheet" href="[PATH]/style/blog.css">  <!-- solo se blog post -->
</head>
```

`[PATH]` dipende dalla posizione della pagina:
- Root (`/`): `./`
- Sottocartelle (`/mainPages/`, `/blogPosts/`, `/subpages/`): `../`

**Non** aggiungere `night_mode.css`, `styling.css`, `footer.css`, `phone.css` — sono già in `base.css`, caricato da `commonHeader.js`.

### Cosa inietta `commonHeader.js` automaticamente
- `base.css` (colori, tipografia, layout, responsive, footer)
- Favicon SVG (`img/icon/favicon.svg`)
- Google Fonts JetBrains Mono
- OG tags generici (title, description, image, url)

### CSS disponibili (da aggiungere manualmente solo se servono)
| File | Quando usarlo |
|------|---------------|
| `style/blog.css` | Blog post con TOC fisso a sinistra |
| `style/img.css` | Pagine con immagini/icone |
| `style/list_div.css` | Pagine con liste di link (stile homepage) |
| `style/button.css` | Pagine con `<button>` |
| `style/table.css` | Pagine con tabelle o `.divTable` |
| `style/gallery.css` | Pagine con slideshow gallery |
| `style/about_me_cards.css` | Solo `aboutme.html` |
| `style/left_right_containers.css` | Layout a due colonne |

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
    <title>Titolo post | Stefano Costa</title>
    <script src="../javascript/commonHeader.js"></script>
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "BlogPosting",
      "headline": "Titolo post",
      "datePublished": "YYYY-MM-DD",
      "author": {"@type": "Person", "name": "Stefano Costa", "url": "https://st-costa.github.io/"},
      "url": "https://st-costa.github.io/blogPosts/Nome%20File.html",
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
<script src="../javascript/toc.js"></script>  <!-- nel <head> -->
<div class="toc"></div>                        <!-- nel <body>, dopo h1/h2 subtitle -->
```

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

### Aggiungere il post a `mainPages/blogFeed.xml`
Aggiungere una nuova `<item>` all'inizio del feed RSS.

### Aggiungere il post a `sitemap.xml`
```xml
<url>
    <loc>https://st-costa.github.io/blogPosts/Nome%20File.html</loc>
    <changefreq>yearly</changefreq>
    <priority>0.7</priority>
</url>
```

---

## Immagini — regole

### Formato
- **Usare sempre WebP** per immagini nuove. Convertire con:
  ```bash
  convert originale.jpg -quality 80 originale.webp
  # oppure per batch:
  find img/ -name "*.jpg" -o -name "*.png" | while read f; do convert "$f" -quality 80 "${f%.*}.webp"; done
  ```
- Eccezione: `preview_image.jpg` resta JPG per compatibilità con crawler OG.

### Lazy loading
- Aggiungere `loading="lazy"` a **tutte** le `<img>`, tranne le icone social sulla homepage (above the fold, ma trascurabile).

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
| Immagini profilo | `img/profili/` |
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

---

## `robots.txt` — cosa è escluso

`/document/`, feed XML, `_template.html`, `Test post.html`, `.claude/`, `.github/`.
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
├── img/              ← immagini (sempre WebP)
└── document/         ← PDF accademici (non indicizzati)
```
