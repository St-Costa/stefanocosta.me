# St-Costa.github.io

Sito personale di Stefano Costa — matematico, sviluppatore, imprenditore.

## Struttura

```
/
├── index.html                  ← Homepage
├── 404.html                    ← Pagina errore custom
├── sitemap.xml                 ← Sitemap per SEO
├── robots.txt                  ← Istruzioni per i crawler
├── CLAUDE.md                   ← Istruzioni per Claude Code
├── mainPages/                  ← Pagine principali (About, Blog, Projects…)
├── blogPosts/                  ← Post del blog (HTML)
│   └── _template.html          ← Template di riferimento per nuovi post
├── subpages/                   ← Approfondimenti accademici
├── style/
│   ├── base.css                ← Colori, tipografia, layout, responsive (caricato da commonHeader.js)
│   ├── components.css          ← Immagini, liste, bottoni, tabelle, layout 2 colonne
│   ├── blog.css                ← TOC fisso, callout, stile post
│   ├── gallery.css             ← Slideshow gallery
│   └── about_me_cards.css      ← Cards nella pagina About
├── javascript/
│   ├── commonHeader.js         ← Inietta base.css, font, favicon, OG tags
│   ├── footer.js               ← Footer dinamico
│   ├── toc.js                  ← Genera TOC automatico dagli heading
│   ├── gallery.js              ← Controlli slideshow
│   └── about_me_cards.js       ← Interazioni cards
├── img/                        ← Immagini (formato WebP preferito)
│   ├── icon/                   ← Icone UI e social
│   ├── blog/                   ← Foto per i post del blog
│   └── profili/                ← Foto profilo
└── document/                   ← PDF accademici (non indicizzati da robots.txt)
```

## Aggiungere un blog post

1. Copiare `blogPosts/_template.html` e rinominare
2. Aggiungere i `data-og-*` sul tag `<script src="...commonHeader.js">` (vedi CLAUDE.md)
3. Aggiungere il link in `mainPages/Blog_pages.html` (in cima alla lista)
4. Aggiungere l'URL in `sitemap.xml`
5. Aggiornare `mainPages/blogFeed.xml`
6. Immagini: usare WebP, aggiungere `loading="lazy"` e `alt`

## Deploy

Automatico via GitHub Actions su push al branch `main`.
Il workflow converte automaticamente PNG/JPG senza corrispondente WebP prima del deploy.
