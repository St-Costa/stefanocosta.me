---
name: pre-commit-review
description: Review pre-commit del sito (meta/alt, contrasto, mobile, peso pagina, link esterni, form/cookie). Usare ogni volta che l'utente chiede di committare, fare commit, controllare le modifiche prima del commit o pubblicare aggiornamenti del sito.
---

# Review pre-commit

Quando l'utente chiede di committare ("committa tutto", "fai commit", ecc.),
**prima** di `git commit` esegui questa review. L'esito è **bloccante**: se un
punto fallisce, correggi e non committare. Niente `--no-verify` di tua
iniziativa: lo usa solo l'utente, per casi eccezionali.

Contesto: sito statico senza tracker, senza cookie, senza form (vedi
`CLAUDE.md` → "Regola numero uno"). Alcuni controlli qui sotto scattano solo
se hai introdotto il caso che li richiede: allora sono obbligatori, altrimenti
segna N/A ed è finita lì.

## Procedura

1. **Perimetro**: `git status --short`, `git diff --cached --name-only`,
   `git diff --name-only` (staged + unstaged). La review qualitativa (§Checklist)
   si concentra sui file cambiati; lo script gira su tutto il sito.
2. **Deterministico**: `python3 scripts/check_site.py`. Ogni `ERRORE` va corretto.
   Gli `avvisi` su file legacy (JPG/PNG esistenti, file >1MB esistenti) sono
   debito noto e non bloccano — ma un file **nuovo o modificato** non deve
   aggiungerne: sulle righe cambiate, gli avvisi valgono come errori.
3. **Qualitativo**: per ogni pagina cambiata, applica la §Checklist con giudizio.
4. **Fix discrezionali: proponi, non applicare.** I fix meccanici bloccanti
   (errori di `check_site.py`: alt mancanti, dimensioni, tag obbligatori) si
   correggono direttamente. Tutto il resto — link esterni da sostituire,
   frasi da riscrivere, immagini da comprimere/cancellare, codice morto da
   rimuovere — va presentato all'utente in una lista così fatta, **un punto
   per fix**, e applicato solo dopo il suo ok:
   - `file:linea` — cosa c'è adesso (con evidenza: HTTP code, output comandi)
   - fix proposto e perché
   - alternative considerate (es. testo semplice senza link, tenere il file)
   - se il fix tocca il testo visibile, riporta prima/dopo della frase
   Non raggruppare fix diversi nello stesso punto: l'utente deve poter dire
   sì a uno e no a un altro. In caso di dubbio (sito che blocca i bot,
   pagina che potrebbe tornare online), default = non toccare, segnala come
   "non verificabile".
5. **Chiudi**: solo se tutto passa, committa (e solo se l'utente l'ha chiesto
   esplicitamente). Se hai cambiato regole (struttura `<head>`, CSS, convenzioni
   su immagini/accessibilità), aggiorna `CLAUDE.md`, `blogPosts/_template.html`
   e questa skill **nello stesso commit** — sono la stessa documentazione.

## Checklist (solo sulle pagine/file cambiati)

- **Secrets**: nelle righe aggiunte (`git diff`) nessun token/chiave/password
  (`AKIA…`, `ghp_…`, `PRIVATE KEY`, `api_key = "…"`, …). Lo script cerca nei file;
  tu controlla anche i contenuti incollati nei post (log, snippet, screenshot).
- **HTTPS**: nessun `href="http://…"` / `src="http://…"` aggiunto. `xmlns="http://…"`
  degli SVG è namespace, non richiesta: ok.
- **Cookie/consent**: solo se hai aggiunto `document.cookie`, `localStorage`,
  analytics o script di terze parti → servono banner di consenso e policy.
  Altrimenti N/A (il sito oggi: zero cookie, zero tracker).
- **Meta**: `<title>` e description specifici della pagina, description 50–160
  caratteri e unica (confrontala con le altre pagine, niente testo generico).
  La lunghezza >160 la blocca già lo script; la qualità la giudichi tu.
- **Social preview**: `og:image` locale ed esistente (lo script verifica il file),
  anteprima sensata per la pagina.
- **Favicon**: `rel="icon"` presente (lo script lo verifica).
- **Sitemap/robots**: pagina nuova → aggiunta a `sitemap.xml` con
  `changefreq`/`priority` giusta (post 0.7, main 0.8–0.9, subpages 0.4–0.5).
  `robots.txt` invariato salvo nuovi path da escludere.
- **Alt text**: ogni `<img>` nuova ha `alt` (lo script verifica la presenza).
  La qualità la giudichi tu: screenshot di testo (tweet, citazioni) → `alt` con
  la **trascrizione** del testo; decorativa con testo adiacente → `alt=""`;
  copertine → titolo dell'opera. Mai "screenshot di…" come descrizione.
- **Compressione**: immagini nuove in WebP (eccezione: `preview_image.jpg`),
  `width`/`height` reali, `loading="lazy"` sotto la piega (mai above the fold),
  indicativo <500KB per file e pagina <2MB di immagini (verifica con `du -sh`).
  Nuovi JPG/PNG o file enormi = blocco.
- **Load speed**: nessun JS/CSS render-blocking aggiunto (`defer` sugli script,
  `base.css` linkato, preload dei 2 font, niente librerie/terze parti).
- **Contrasto**: nuovi colori → WCAG AA (testo normale ≥4.5:1, grande ≥3:1).
  Calcola il rapporto o verifica in DevTools. Palette esistente: fondo scuro,
  testo chiaro, giallo `#FBFFAD` per gli `<i>`.
- **Mobile**: `viewport` presente (lo script lo verifica); niente larghezze fisse
  >360px senza media query; TOC fisso e gallery utilizzabili da stretto
  (i breakpoint stanno in `base.css`, prima della sezione Responsive non
  aggiungere regole che li scavalcano).
- **Link rotti**: i locali li blocca già lo script. Per ogni link **esterno**
  nuovo o cambiato: verifica che risponda (`curl -sI -o /dev/null -w "%{http_code}"`
  o webfetch) e che ogni ancora `#id` esista nella pagina di destinazione.
- **Form**: solo se hai aggiunto un `<form>` → `<label>` + `name` su ogni campo
  (lo script li verifica), validazione HTML5 (`required`, `type`, `pattern`) o JS
  con messaggi d'errore. Altrimenti N/A (il sito oggi non ha form).
- **Spam**: solo se il form invia dati (POST o action esterna) → honeypot,
  captcha o Turnstile. Altrimenti N/A (niente commenti, niente embed).

## Checklist finale prima di committare

- [ ] `python3 scripts/check_site.py`: 0 errori; nessun avviso nuovo da file cambiati.
- [ ] Meta/alt delle pagine cambiate: specifici, non generici, alt dei testi-immagine trascritti.
- [ ] Immagini nuove: WebP, dimensioni reali, lazy corretto, peso ok.
- [ ] Contrasto dei nuovi colori ≥4.5:1; layout verificato da stretto.
- [ ] Link esterni nuovi/ cambiati: rispondono; ancore esistenti.
- [ ] Form/cookie/consent: gestiti se introdotti, altrimenti N/A dichiarato.
- [ ] Pagina nuova: `sitemap.xml` (+ `Blog_pages.html` / feed se post, vedi `CLAUDE.md`).
- [ ] Nessun secret nelle righe aggiunte.
- [ ] Nessun commit automatico oltre quello richiesto.
