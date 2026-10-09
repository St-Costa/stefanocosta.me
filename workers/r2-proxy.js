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
//   lettori PDF non caricano le pagine in modo incrementale. I range vanno
//   sempre a R2 (freschi), non in cache: sono piccoli e rari.
// - Edge cache IN-WORKER (caches.default): le risposte 200 intere si cachano
//   all'edge per un anno. È sicuro perché le chiavi non si sovrascrivono MAI
//   (nuova versione = nuovo nome file, vedi CLAUDE.md §File pesanti e R2).
//   L'header X-Worker-Cache dice HIT / MISS / BYPASS (range) / HEAD.
//   I 404 non si cachano mai: un file appena caricato è subito disponibile.
// - Cache-Control immutable: stessa garanzia esposta ai browser/CDN.
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

function baseHeaders(meta, key, route) {
  const headers = new Headers();
  headers.set("Content-Type", meta.httpMetadata?.contentType || guessContentType(key));
  headers.set("Accept-Ranges", "bytes");
  headers.set("Cache-Control", "public, max-age=31536000, immutable");
  headers.set("X-Content-Type-Options", "nosniff");
  headers.set("ETag", meta.httpMetadata?.etag || meta.etag);
  if (route.noindex) {
    headers.set("X-Robots-Tag", "noindex");
  }
  return headers;
}

export default {
  async fetch(request, env, ctx) {
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

    // HEAD: bastano i metadati (niente lettura del corpo da R2).
    if (request.method === "HEAD") {
      const meta = await bucket.head(key);
      if (!meta) {
        return new Response("Not found", { status: 404 });
      }
      const headers = baseHeaders(meta, key, route);
      headers.set("Content-Length", String(meta.size));
      headers.set("X-Worker-Cache", "HEAD");
      return new Response(null, { status: 200, headers });
    }

    // Range tipo "bytes=1234-" o "bytes=1234-5678": sempre da R2, mai in
    // cache. Altri formati (es. "bytes=-500") si ignorano servendo il file
    // intero (200): è legale e i browser riprovano con un range semplice.
    const m = /^\s*bytes=(\d+)-(\d*)\s*$/.exec(request.headers.get("Range") || "");
    if (m) {
      const obj = await bucket.get(key, {
        range: {
          offset: Number(m[1]),
          length: m[2] === "" ? undefined : Number(m[2]) - Number(m[1]) + 1,
        },
      });
      if (!obj || !obj.range) {
        return new Response("Not found", { status: 404 });
      }
      const headers = baseHeaders(obj, key, route);
      const start = obj.range.offset;
      headers.set("Content-Range", `bytes ${start}-${start + obj.range.length - 1}/${obj.size}`);
      headers.set("Content-Length", String(obj.range.length));
      headers.set("X-Worker-Cache", "BYPASS");
      return new Response(obj.body, { status: 206, headers });
    }

    // GET intero: prima la cache edge, poi R2 (e si mette in cache).
    const cache = caches.default;
    const cacheKey = new Request(url.toString(), { method: "GET" });
    const cached = await cache.match(cacheKey);
    if (cached) {
      const hit = new Response(cached.body, cached);
      hit.headers.set("X-Worker-Cache", "HIT");
      return hit;
    }

    const obj = await bucket.get(key);
    if (!obj) {
      return new Response("Not found", { status: 404 });
    }
    const etag = obj.httpMetadata?.etag || obj.etag;
    const headers = baseHeaders(obj, key, route);

    // 304 se il client ha già la copia corrente (non si cacha il 304).
    if (request.headers.get("If-None-Match") === etag) {
      return new Response(null, { status: 304, headers });
    }

    headers.set("Content-Length", String(obj.size));
    headers.set("X-Worker-Cache", "MISS");
    const response = new Response(obj.body, { status: 200, headers });
    // Scrittura in cache in background: la risposta parte subito.
    ctx.waitUntil(cache.put(cacheKey, response.clone()).catch(() => {}));
    return response;
  },
};
