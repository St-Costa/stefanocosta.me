// workers/redirect.js
//
// Redirect permanente (301) dal vecchio dominio a costeve.com.
// Mantiene path e query string:
//   stefanocosta.me/mainPages/aboutme.html?x=1
//   -> https://costeve.com/mainPages/aboutme.html?x=1
//
// Deploy:
//   cd workers && wrangler deploy -c wrangler.redirect.toml
//
// Le route coprono apex e www del vecchio dominio. Il Worker R2
// (r2-proxy.js) usa solo le route del nuovo dominio: così anche i vecchi
// URL /document/* e /audio/* passano da qui e vengono rediretti.

const TARGET_ORIGIN = "https://costeve.com";

export default {
  fetch(request) {
    const url = new URL(request.url);
    const target = new URL(TARGET_ORIGIN);
    // Setter (non concatenazione): evita che un path che inizia con "//"
    // venga interpretato come un host esterno.
    target.pathname = url.pathname;
    target.search = url.search;
    return Response.redirect(target.toString(), 301);
  },
};
