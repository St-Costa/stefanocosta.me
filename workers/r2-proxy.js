// workers/r2-proxy.js
//
// Serve i due bucket R2 dallo STESSO dominio del sito, così gli URL pubblici
// non cambiano e restano first-party (regola n°1 salva):
//   stefanocosta.me/document/*  ->  bucket stefanocosta-documents
//   stefanocosta.me/audio/*      ->  bucket stefanocosta-audio
//
// I bucket restano PRIVATI (niente accesso pubblico R2): l'unica via
// d'ingresso è questo Worker. Niente directory listing: solo chiavi esatte.
//
// Dettagli che contano e perché:
// - Range requests (206): senza, <audio> non può saltare avanti/indietro e i
//   lettori PDF non caricano le pagine in modo incrementale.
// - Cache-Control immutable: le chiavi non si sovrascrivono MAI (nuova
//   versione = nuovo nome file, vedi CLAUDE.md §File pesanti e R2), quindi si
//   può cachare all'edge per un anno senza rischi di stale.
// - X-Robots-Tag: noindex su /document/*: cintura + bretelle oltre al
//   Disallow di robots.txt (i PDF accademici non vanno indicizzati).
//
// Deploy:  cd workers && wrangler deploy   (vedi wrangler.toml qui accanto)

const ROUTES = [
  { prefix: "/audio/", binding: "AUDIO", noindex: false },
  { prefix: "/document/", binding: "DOCUMENTS", noindex: true },
];

const CONTENT_TYPES = {
  pdf: "application/pdf",
  mp3: "audio/mpeg",
  wav: "audio/wav",
  m4a: "audio/mp4",
  ogg: "audio/ogg",
  opus: "audio/ogg",
  flac: "audio/flac",
  aac: "audio/aac",
};

function guessContentType(key) {
  const ext = key.split(".").pop().toLowerCase();
  return CONTENT_TYPES[ext] || "application/octet-stream";
}

export default {
  async fetch(request, env) {
    if (request.method !== "GET" && request.method !== "HEAD") {
      return new Response("Method not allowed", { status: 405 });
    }

    const url = new URL(request.url);
    const route = ROUTES.find((r) => url.pathname.startsWith(r.prefix));
    if (!route) {
      return new Response("Not found", { status: 404 });
    }

    const bucket = env[route.binding];
    if (!bucket) {
      return new Response("R2 binding mancante", { status: 500 });
    }

    const key = decodeURIComponent(url.pathname.slice(route.prefix.length));
    if (!key || key.endsWith("/") || key.includes("..")) {
      return new Response("Not found", { status: 404 });
    }

    // Range tipo "bytes=1234-" o "bytes=1234-5678". Altri formati (es. i
    // suffissi "bytes=-500") si ignorano servendo il file intero (200):
    // è legale per lo standard e i browser riprovano con un range semplice.
    let range = null;
    const m = /^\s*bytes=(\d+)-(\d*)\s*$/.exec(request.headers.get("Range") || "");
    if (m) {
      range = { offset: Number(m[1]), length: m[2] === "" ? undefined : Number(m[2]) - Number(m[1]) + 1 };
    }

    const obj = range ? await bucket.get(key, { range }) : await bucket.get(key);
    if (!obj) {
      return new Response("Not found", { status: 404 });
    }

    const headers = new Headers();
    headers.set("Content-Type", obj.httpMetadata?.contentType || guessContentType(key));
    headers.set("Accept-Ranges", "bytes");
    headers.set("Cache-Control", "public, max-age=31536000, immutable");
    headers.set("X-Content-Type-Options", "nosniff");
    headers.set("ETag", obj.httpMetadata?.etag || obj.etag);

    // 304 se il client ha già la copia corrente.
    if (request.headers.get("If-None-Match") === (obj.httpMetadata?.etag || obj.etag)) {
      return new Response(null, { status: 304, headers });
    }

    if (range && obj.range) {
      const start = obj.range.offset;
      const end = start + obj.range.length - 1;
      headers.set("Content-Range", `bytes ${start}-${end}/${obj.size}`);
      headers.set("Content-Length", String(obj.range.length));
      return new Response(request.method === "HEAD" ? null : obj.body, {
        status: 206,
        headers,
      });
    }

    if (route.noindex) {
      headers.set("X-Robots-Tag", "noindex");
    }
    headers.set("Content-Length", String(obj.size));
    return new Response(request.method === "HEAD" ? null : obj.body, {
      status: 200,
      headers,
    });
  },
};
