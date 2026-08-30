---
name: obsidian-to-post
description: Traduce una nota Obsidian (>[!callout], [[wikilink]], ^[footnote]) in un post HTML del blog, normale o "unlisted" (non listato/senza RSS, tipico dei post-mortem linkati dal failure resume). Usare ogni volta che l'utente fornisce un file .md scritto in Obsidian e chiede di trasformarlo in un post del sito, listed o unlisted.
---

# Da nota Obsidian a post del blog

Questa skill vale per **qualsiasi** post che nasce da una nota Obsidian, non solo quelli
"nascosti" del failure resume. Le regole di formattazione (§Regole) sono generali: fusione
paragrafi, callout, footnote, wikilink, virgolette. La sezione §Se il post è unlisted si
applica solo quando l'utente chiede esplicitamente un post non listato/senza RSS (tipicamente
un post-mortem linkato da `Failure_resume.html`) — per un post normale, saltala e segui la
procedura standard di pubblicazione del blog (`Blog_pages.html`, `gen_feed.py`, ecc., vedi
`CLAUDE.md` → "Blog post — checklist aggiuntiva").

Le regole qui sotto sono state ricavate a mano, post-mortem per post-mortem (letteralmente), da
una sessione in cui la prima traduzione ha sbagliato quasi tutto. Seguile alla lettera: sono
meccaniche dove possono esserlo, e segnalano esplicitamente dove serve giudizio.

## Procedura

1. **Crea il file** `blogPosts/<Titolo post>.html` usando `blogPosts/_template.html` come base
   per l'head (preload font, OG tag, favicon, `toc.js`, `blog.css`).
2. **Header del post**: `<h1>` = titolo, `<h2 class="subtitle">` = sottotitolo (chiedi
   all'utente la formulazione esatta, non inventarla), `<h3 class="subtitle">` = epistemic status
   con link a `https://forum.effectivealtruism.org/posts/bbtvDJtb6YwwWtJm7/epistemic-status-an-explainer-and-some-thoughts`.
   Nel `div.center`: data (mese esteso in inglese + anno, es. "August 2026" — mai solo l'anno),
   conteggio parole/tempo di lettura, e il link "Other posts" (verso `Blog_pages.html`, salvo
   il caso unlisted — vedi sotto).
3. **TL;DR**: scrivilo tu, breve (2–3 frasi), zero AI-slop (niente triplette a effetto tipo
   "X, Y, and Z", niente frase-sentenza chiusa a effetto). Diretto, concreto, con l'esito e
   il perché in due mosse.
4. **Traduci il corpo** seguendo le regole di formattazione sotto.
5. Se il post è **unlisted**, applica anche i passaggi in §Se il post è unlisted. Altrimenti
   segui la checklist standard di pubblicazione (`Blog_pages.html`, `sitemap.xml`,
   `python3 scripts/gen_feed.py`).
6. **Esegui `python3 scripts/check_site.py`** e correggi tutto prima di fermarti.
7. **Non committare** se non richiesto esplicitamente.

---

## Regole di formattazione (il cuore della skill)

### Fondere i paragrafi: la regola più importante e la più violata

Nella nota Obsidian, un "a capo singolo" (fine riga, niente riga vuota dopo) e un
"paragrafo vuoto" (riga vuota tra due blocchi) sono **entrambi resi dentro lo stesso `<p>`**,
mai con `<p>` separati. Il sito non spezza mai un blocco di prosa continua in più `<p>`: lo fa
solo quando cambia davvero contesto (nuova lista, nuovo callout, nuovo header, `<hr>`).

Verificalo sempre su un post reale prima di fidarti a memoria — es.
`blogPosts/June Monthly Business Ahas.html`, sezione "Understand the sea before you fish".

- **A capo singolo nel `.md`** (riga che finisce e la successiva inizia subito, senza riga
  vuota) → `<br>` singolo, **senza riga vuota HTML**, appiccicato alla riga precedente:
  ```html
  <br>Testo della riga successiva.
  ```
- **Riga vuota nel `.md`** (paragrafo separato in Obsidian) → `<br><br>` (doppio), sempre
  dentro lo **stesso** `<p>`:
  ```html
  Fine del paragrafo A.
  <br><br>
  Inizio del paragrafo B.
  ```
- **Mai** un `<br>` isolato tra due `<p>` separati: se serve isolarlo, la riga vuota va
  dentro il `<p>` esistente come `<br><br>`, non tra due `<p>` diversi.

Prima di scrivere anche solo una riga, genera la mappa completa del `.md` (blank vs non-blank)
con qualcosa come:
```python
for i, line in enumerate(text.split("\n"), 1):
    marker = "  <<<< BLANK" if line.strip() == "" else ""
    print(f"{i:4}{marker} {line}")
```
e traduci riga per riga da quella mappa, non a memoria/interpretazione.

### Liste

`- voce` markdown → `<ul><li>...</li></ul>` **senza** `class="content_list"` (quella classe è
per `Projects.html`/`Failure_resume.html`, non per i post del blog — lì una `<ul>` nuda eredita
lo stile corretto da `base.css`). Se la lista è preceduta da un paragrafo introduttivo separato
da riga vuota nel `.md`, il paragrafo diventa un `<p>` a sé con `<br><br>` iniziale prima del
testo (vedi esempio sopra), non fuso nel testo della lista.

### Callout Obsidian → `.callout`

`>[!tipo] Titolo` diventa:
```html
<section class="callout">
    <div class="box-title">
        <h4>Titolo</h4>
    </div>
    <p class="justify">Riga 1.
        <br>Riga 2.
        <br>Riga 3.</p>
</section>
```
Dentro il callout, le righe **non hanno mai riga vuota tra loro** in Obsidian (i callout sono
blocchi `>` compatti), quindi tutte le righe interne prendono `<br>` singolo, appiccicate
(niente `<br><br>` dentro un callout salvo che il `.md` lo richieda esplicitamente).

Icone dei box-title, **solo se già previste**:
- `>[!quote]` → `<div class="box-title"><img width="32" height="32" loading="lazy" class="icon_inline" src="../img/icon/quotes.png" alt=""><h4>Quote</h4></div>`
- Warning/avvertimento → `img/icon/warning.png`, stesso schema.
- **Tipi non standard** (es. Obsidian `>[!remark]`, che il sito non conosce): mantieni il
  titolo esatto che l'autore ha scritto (es. "Remark", "Economical remark") — non tradurlo
  in "Warning". Chiedi se vuole comunque l'icona warning per dare peso visivo, ma il titolo
  del box resta quello originale, mai sostituito.

### Footnote (`^[testo]`)

**Non** creare una sezione "Notes" a fine pagina con numeri e rimandi. Le footnote di questo
sito sono **davvero inline**: tutto il contenuto della nota (testo e link compresi) va dentro
un `<sup>` posizionato esattamente dove appare nel testo originale, **prima del punto finale**
della frase, racchiuso tra `[...]`:
```html
Testo della frase<sup>[Read <a href="URL" target="_blank">this</a>]</sup>.
```
Se la nota ha più link (es. `^[Read [this](url1) and [this](url2)]`), tutti dentro lo stesso
`<sup>`. Se il markdown scrive "Read"/"See" prima del link, mantienilo dentro le `[...]`.

### Wikilink `[[...]]` — qui serve giudizio, non automazione

Non esiste una regola meccanica: ogni wikilink va risolto guardando cosa referenzia.
Casistica osservata finora, in ordine di frequenza:

1. **`[[(Stefano blog) Titolo post]]`** → è un post del blog. Cerca il file:
   `grep -rl "Titolo" blogPosts/*.html`. Il link nell'HTML finale è **relativo, senza
   `../`** se il file di destinazione è nella stessa cartella `blogPosts/` (es.
   `<a href="I am not a mathematician.html">testo</a>`).
2. **`[[Titolo libro (anno) - Autore]]`** → verifica prima se il sito lo linka già altrove
   (`grep -rli "titolo libro" blogPosts/*.html`) e riusa lo stesso URL esterno per coerenza
   (spesso Goodreads o il sito dell'editore). Se non trovi nulla, chiedi.
3. **`[[Mese Monthly Aha's#Sezione|testo visibile]]`** → link a una sezione di un post MBA.
   Gli `id` delle sezioni sono progressivi (`h1.1`, `h1.2`, ...), **non derivabili dal
   titolo**: cerca `grep -n -A1 '<h2 id="h.*\.' "blogPosts/<Mese> Monthly Business Ahas.html"`
   e abbina per testo dell'header. Link risultante:
   `<a href="<Mese> Monthly Business Ahas.html#hN.M">testo</a>`.
4. **`[[Progetto]]`** che corrisponde a una voce di `Projects.html` o `Failure_resume.html`
   → linka **solo la parte di testo prima dei `:`** (se la frase ha la forma
   "Nome progetto: descrizione"), verso `../mainPages/Projects.html#id-progetto` (o
   `Failure_resume.html`). **Prima di linkare, verifica che l'`id` sia univoco**:
   ```bash
   grep -c 'id="NomeId"' mainPages/Projects.html
   ```
   Diverse voci di `Projects.html` condividono per errore lo stesso `id` (es. `id="Ashlight"`
   copiaincollato su 4 progetti diversi). Se è duplicato, **correggi prima l'id in
   `Projects.html`** dandogli uno slug univoco derivato dal titolo del progetto, poi linka.
   Non linkare mai a un `id` duplicato senza prima sistemarlo: punterebbe al progetto
   sbagliato (il browser risolve sempre al primo match).
5. **Wikilink isolato, senza contesto chiaro nel testo circostante** (es. una riga a sé
   stante a fine documento, tipo `[[Libro]] ERRORE ...`) → non forzarlo in nessun punto del
   post pubblicato. Segnalalo esplicitamente all'utente invece di indovinare dove piazzarlo.

### Enfasi e virgolette

- `**bold**` → `<b>`.
- `_corsivo_` / `*corsivo*` → **`<i>` solo se è enfasi vera** (termine coniato, tesi,
  concetto): sul sito `<i>` è **giallo** (`i, .yellow { color: #FBFFAD }`). Se il corsivo è
  "di tono" — battuta riportata tra `"…"`, titolo di libro/opera, scare-quote — usa `<em>`
  (corsivo senza colore). Regola: se è già tra virgolette, `<em>`. Vedi CLAUDE.md §"Corsivi".
- Le virgolette doppie del markdown (`"..."`) vanno **sempre convertite in virgolette curve**
  (`“…”`), mai lasciate dritte — controlla tutto il post alla fine con
  `grep -n '"' file.html` per scovare quelle rimaste dritte per distrazione.
- `\-` a inizio riga (escape Obsidian) è un trattino letterale, non un bullet: non
  trasformarlo in `<li>`.

---

## Se il post è unlisted

Applica questa sezione **solo** se l'utente chiede esplicitamente un post non listato/senza
RSS — tipicamente un post-mortem che sarà linkato da una voce del failure resume
(`mainPages/Failure_resume.html`). Per un post normale del blog, ignora questa sezione.

1. **Marca il post come unlisted**, nel `<head>` al posto del JSON-LD con `datePublished`:
   ```html
   <!-- unlisted-post: not in Blog_pages.html, no datePublished (keeps it out of
        gen_feed.py's RSS feed), only reachable via a direct link. -->
   ```
   Non aggiungerlo a `Blog_pages.html`, non serve `gen_feed.py`. Aggiungilo comunque a
   `sitemap.xml` (non è privato, solo fuori dalle liste pubbliche — `changefreq yearly`,
   `priority 0.7`).
2. Nel `div.center` dell'header, il link finale punta **a `../mainPages/Failure_resume.html`**
   invece del solito "Other posts" verso `Blog_pages.html`.
3. **Aggiungi la entry nel failure resume** (`mainPages/Failure_resume.html`), stesso pattern
   delle altre voci (`<h3 class="inline">Titolo,</h3><h4 class="inline"><i>Tipo</i></h4>`),
   con `<h5>` che linka al post completo, e un `<img class="project_type_logo">` se esiste un
   logo pertinente (marchio del progetto/business, non un'icona generica — vedi §Logo sotto).
4. Vedi anche `CLAUDE.md` → "Post nascosti (unlisted)" per la convenzione completa.

### Logo nella entry del failure resume

Se il post-mortem riguarda un business/progetto con un brand riconoscibile (sito web, logo),
prova a recuperare il logo **quadrato più grande disponibile**, non la favicon piccola:
1. Fetcha l'HTML del sito, cerca `<link rel="apple-touch-icon">` o `<link rel="icon"
   sizes="192x192">`.
2. Prova a risalire al file sorgente non ridimensionato/croppato (spesso i CMS servono
   `nome-WxH.ext` a partire da un `nome.ext` originale — prova a togliere il suffisso
   dimensione e le varianti `@2x`/`cropped-`).
3. Salvalo in `img/icon/<nome-progetto>.webp` (convertito via ImageMagick, come da regola
   generale del sito sulle immagini).
4. Usalo come `<img class="project_type_logo" ...>` nella entry, stesso pattern delle altre
   (`width`/`height` reali, `loading="lazy"`, `alt` col nome del brand).

## Checklist finale prima di fermarti

- [ ] Mappa blank/non-blank del `.md` generata e seguita riga per riga, non a memoria.
- [ ] Nessun `<p>` spezzato dove il `.md` aveva solo una riga vuota tra frasi correlate.
- [ ] Liste senza `content_list`.
- [ ] Footnote inline con `[...]` prima del punto, non una sezione Notes.
- [ ] Wikilink risolti uno per uno, non a naso; `id` duplicati in `Projects.html` corretti.
- [ ] Virgolette tutte curve.
- [ ] `python3 scripts/check_site.py` pulito.
- [ ] Se listed: aggiunto a `Blog_pages.html`, `sitemap.xml`, feed rigenerato con `gen_feed.py`.
- [ ] Se unlisted: marcatore `unlisted-post`, entry nel failure resume, logo se pertinente.
- [ ] Nessun commit automatico.
