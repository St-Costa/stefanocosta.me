# Code improvements — backlog

## 🔴 Alta priorità

_Tutti gli item di alta priorità sono stati completati._

---

## 🟡 Media priorità

### CSS
- **Un solo breakpoint responsive (950px)** — `phone.css` ha un solo breakpoint. Aggiungere almeno 480px e 768px per coprire tablet e telefoni piccoli.
- **Stili inline residui nell'HTML**:
  - `mainPages/colophon.html` righe 22–38: `style="background-color: ..."` su ogni cella della tabella → estrarre in classi CSS
  - `blogPosts/Things from Graz.html`: `style="padding: 13px;"` ripetuto 16+ volte → creare classe `.center-padding`
  - `mainPages/Projects.html` riga 185: `#ccc` hardcoded inline → usare variabile CSS
- **Dipendenza circolare CSS** — `style/button.css` e `style/list_div.css` importano entrambi `night_mode.css`, che viene già caricato da `commonHeader.js`. Rimuovere i `@import` ridondanti.
- **`!important` residui in phone.css** — `.index_img`, `.poster_table td`, `.footer_index`, `.divTd`, `.image_divTd`, `.list_span` hanno ancora `!important` perché i loro CSS di pagina vengono caricati dopo `phone.css`. Valutare se ristrutturare l'ordine di caricamento.

### JavaScript
- **Nessuna gestione degli errori** — `gallery.js`, `toc.js`, `about_me_cards.js` manipolano il DOM senza verificare che gli elementi esistano. Aggiungere null check minimi.
- **`toc.js` riga 8**: `if (index < 2) return;` — salta i primi 2 header senza commento esplicativo. Chiarire l'intenzione.

### HTML
- **`styling.css` duplicato nelle pagine `mainPages/`** — analogamente a quanto fatto per i blog post, le pagine in `mainPages/` hanno ancora `<link href="../style/styling.css">` inline anche se già caricato da `commonHeader.js`. Non causa bug (a differenza dei blog post) ma è ridondante.
- **Gerarchia heading inconsistente** — alcune pagine saltano livelli (H1 → H3) o usano H3 dove sarebbe appropriato H2. Revisione pagina per pagina.

---

## 🟢 Bassa priorità

### Naming e convenzioni
- ~~**Classi CSS con nomi italiani**~~ — **COMPLETATO**: `.giustifica` rinominato `.justify` in tutti i CSS e HTML; commenti italiani in `phone.css` e `list_div.css` tradotti in inglese.
- ~~**Scala di spaziatura ad hoc**~~ — **COMPLETATO**: aggiunte variabili `--space-sm` / `--space-md` / `--space-lg` in `:root` (`night_mode.css`); `list_div.css` aggiornato per usarle.

### Template e duplicazione
- ~~**Pattern HTML ripetuto nei blog post**~~ — **COMPLETATO**: creato `blogPosts/_template.html` con struttura base (head, TOC, TL;DR, sezioni H2/H3, callout commentati).
- **Icone social** — lo stesso pattern `<a><img class="icon animated_img"></a>` appare in `index.html` e `mainPages/Blog_pages.html`. Se dovesse comparire in altre pagine, considerare un componente condiviso.

### Performance
- **12 file CSS separati** — caricamento di 12 `<link>` separati per ogni pagina. Valutare un bundle minificato per produzione (opzionale su un sito statico piccolo).
- ~~**Immagini icone**~~ — **INVESTIGATO, NON RIMUOVERE**: `external-link_white.png` è usata in `night_mode.css` (link hover), e le altre (`linkedin_white.png`, `Bluesky_white.png`, `X_white.png`, `github_white.png`, `rss_white.png`) sono usate in `mainPages/colophon.html`. Non sono eliminabili.

---

## Note tecniche

### Perché blog.css usa `body h2` invece di `h2`
I fogli di stile iniettati da `commonHeader.js` via JS (night_mode.css, styling.css, ecc.) vengono applicati dal browser **dopo** i `<link>` inline dell'HTML, anche se appaiono prima nel DOM. Per garantire che le regole di `blog.css` vincano sulla cascade senza usare `!important`, si usa il prefisso `body` / `html body` che aumenta la specificità da `(0,0,1)` a `(0,0,2)`.

### Colophon link rotto (fixato)
Le pagine in `subpages/` avevano il link "Colophon" nel footer puntare a `./colophon.html` (che non esiste in `subpages/`). Ora `footer.js` rileva il contesto e usa `../mainPages/colophon.html` per subpages e blogPosts.

### fieldset decorativo → section + .box-title (completato)
Tutti i `<fieldset>` usati a scopo decorativo (`.briefAboutMe`, `.toc`, `.tldr`, `.callout`, `.explanation_box`) sono stati sostituiti con `<section>` o `<div>`. L'effetto visivo del `<legend>` flottante sul bordo è replicato in CSS con `.box-title { position: absolute; top: 0; left: 50%; transform: translate(-50%, -50%); }` sul contenitore con `position: relative`. Il `.toc` usa un `.toc-scroll` interno per gestire `overflow-y: auto` senza tagliare il `.box-title`.
