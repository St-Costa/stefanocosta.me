# Code improvements — backlog

## 🔴 Alta priorità

_Tutti gli item di alta priorità sono stati completati._

---

## 🟡 Media priorità

### CSS
- ~~**Un solo breakpoint responsive (950px)**~~ — **COMPLETATO**: aggiunti breakpoint `768px` (tablet) e `480px` (telefoni piccoli) a `phone.css`.
- ~~**Stili inline residui nell'HTML**~~ — **COMPLETATO**:
  - `colophon.html`: celle colore → classi `.color-swatch-*` in `table.css` con variabili CSS.
  - Blog post: `style="padding: 13px;"` → classe `.center-padding` in `blog.css` (aggiornati tutti i blog post).
  - `Projects.html`: divider con `#ccc` → classe `.section-divider` in `styling.css` con `var(--text-color)`.
- ~~**Dipendenza circolare CSS**~~ — **COMPLETATO**: rimossi `@import url('night_mode.css')` da `button.css` e `list_div.css`.
- **`!important` residui in phone.css** — **ANALISI**: i fogli JS-iniettati da `commonHeader.js` vengono applicati DOPO i `<link>` inline, quindi `phone.css` dovrebbe già vincere senza `!important`. Appaiono ridondanti ma rimuoverli richiede testing cross-browser. Lasciare invariato.

### JavaScript
- ~~**Nessuna gestione degli errori**~~ — **COMPLETATO**: aggiunti null check in `toc.js` (guard su `.toc`) e `gallery.js` (guard su `slides`, `prev`, `next`, `caption`). `about_me_cards.js` era già robusto.
- ~~**`toc.js` riga 8**: `if (index < 2) return;`~~ — **COMPLETATO**: aggiunto commento esplicativo: salta H2/H3 del titolo e sottotitolo.

### HTML
- ~~**`styling.css` duplicato nelle pagine `mainPages/`**~~ — **COMPLETATO**: rimosso `<link href="../style/styling.css">` da `Academic_past.html` e `Blog_pages.html`.
- ~~**Gerarchia heading inconsistente**~~ — **COMPLETATO**: corretti `Thesis.html` (H2→H4 → H2→H3) e `Academic_projects.html` (H1→H3 → H1→H2→H3→H4). Blog post e altre pagine avevano già gerarchia corretta.

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
