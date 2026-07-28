---
name: new-mba-post
description: Crea un nuovo post mensile "MBA" (Monthly Business Aha's) del blog, con tutti i link collegati (Blog_pages, sitemap, feed RSS). Usare quando l'utente chiede di creare il post MBA di un dato mese.
---

# Nuovo post MBA

I post MBA sono la serie mensile "Monthly Business Aha's". Un post per mese, **pubblicato il 1° del mese successivo** a quello di cui parla (es. "June MBA" → `datePublished` 2026-07-01).

## Convenzioni fisse

- **Nome file**: `blogPosts/<Month> Monthly Business Ahas.html` (mese in inglese, senza apostrofo)
- **Titolo visibile / headline / og-title**: `<Month> MBA`
- **`<title>`**: `<Month> MBA | Source of Truth`
- **URL canonico**: `https://stefanocosta.me/blogPosts/<Month>%20Monthly%20Business%20Ahas.html`
- **meta description / og-description / JSON-LD description**: `<Month> <YYYY> business insights and lessons learned by Stefano Costa.`
- **Epistemic status**: sempre `field notes from one month of experience`

## Procedura

1. **Copia il post MBA più recente** come template (es. `blogPosts/June Monthly Business Ahas.html`) e aggiorna mese, date, URL, subtitle, TL;DR, sezioni.
   - Struttura del `<body>`: `h1` → `h2.subtitle` → `h3.subtitle` (epistemic) → `div.center` (data / `N words - M min read` / link "Other posts") → `section.toc` → `section.tldr` → sezioni.
   - Ogni sezione: `<h2 id="hN.M"><a href="#hN.M">■ Titolo</a></h2>` seguita da `<p class="justify">`, chiusa da `<hr>`.
   - Il TOC si genera da solo (`toc.js`), non scriverlo a mano.
   - Se il testo dell'utente non è ancora arrivato, crea lo scheletro con placeholder (`SUBTITLE`, `TLDR`, `SECTION 1`, `CONTENT`) e riempilo dopo.
2. **Conta le parole** del corpo del post e aggiorna `div.center`: `<em>N words</em> - <em>M min read</em>` (M ≈ N/200, arrotondato).
3. **`mainPages/Blog_pages.html`**: aggiungi `<li><h2><a href="../blogPosts/<Month> Monthly Business Ahas.html"><Month> MBA [YYYY-MM-DD]</a></h2></li>` nella lista, **ordinata per data decrescente** (attenzione: non sempre in cima — verifica le date dei post vicini).
4. **`sitemap.xml`**: aggiungi in cima al blocco `<!-- Blog posts -->` un `<url>` con `changefreq yearly` e `priority 0.7`, URL percent-encoded.
5. **Immagini**: SVG in `img/blog/Monthly MBA/`, inserite con:
   ```html
   <div class="single-image-container">
       <div class="center center-padding"><i class="caption"></i></div>
       <img loading="lazy" src="../img/blog/Monthly MBA/nome.svg" alt="...">
   </div>
   ```
   ⚠️ **Il sito è solo dark mode**: `base.css` imposta `--background-color: #3E3E3E` e `--text-color: #D7D7D7`,
   senza `prefers-color-scheme` né toggle. Gli SVG esportati da editor esterni arrivano spesso con testo nero
   (`fill:rgb(11, 11, 11)`, `fill="black"`) e un `<rect fill="white">` di sfondo: sul fondo grigio scuro il testo
   nero ha contrasto ~1.9:1, illeggibile. Prima di pubblicare un SVG:
   - rimuovi il `<rect x="0" y="0" ... fill="white"/>` di sfondo a piena tela;
   - sostituisci i fill/stroke scuri con `#d3d3d3` (contrasto 7.1:1) — come già fa `Framework matrix.svg`;
   - attenzione: un `style="fill:..."` inline **vince** sull'attributo `fill="..."`, quindi un elemento con
     `fill="#7FCEF0"` ma `style="fill:rgb(11,11,11)"` renderizza nero, non ciano. Allinea i due.
   - palette del sito: ciano `#7FCEF0` (6.1:1), grigi `#d3d3d3` / `#D7D7D7` (7.1–7.4:1).
6. **Mai embed di terze parti** nel post: niente `<script>` di X/Twitter, niente `<iframe>`
   YouTube, niente `<img src="https://...">`. Un tweet va inserito come screenshot locale in
   `img/blog/Monthly MBA/`, dentro `<a class="tweet-shot" href="<url>">`, con l'`alt` che
   riporta il testo del tweet. Il commit fallisce se resta una richiesta esterna.
7. **Feed RSS**: `python3 scripts/gen_feed.py` — mai modificare `mainPages/blogFeed.xml` a mano.
   I controlli su `<main>`, OG tag, preload, link rotti e `datePublished` girano da soli
   al commit (hook pre-commit). Per anticiparli: `python3 scripts/check_site.py`.
8. **Link Obsidian → link interni**: il testo sorgente contiene link stile `[[Mese Monthly Aha's#Titolo sezione]]`.
   Convertili in `<a href="./<Mese> Monthly Business Ahas.html#hN.M">Mese MBA &gt; Titolo sezione</a>`.
   Gli `id` non sono derivabili dal titolo: sono progressivi (`h1.1`, `h1.2`, ...). Ricavali con
   `grep -n -A2 '<h2 id=' "blogPosts/<Mese> Monthly Business Ahas.html"` e abbina per titolo.
9. Non committare se non richiesto.
