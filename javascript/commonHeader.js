// Safety net, not a dependency.
//
// Pages declare their own favicon, Open Graph tags and base.css link directly in
// the HTML: crawlers do not reliably run JavaScript, and anything this file adds
// would arrive too late for the first paint anyway. That is why it is loaded with
// `defer` and never blocks rendering.
//
// It stays around so that a page which forgets one of those tags still gets it,
// rather than shipping unstyled or without a preview image. Each check is a no-op
// on a correctly written page.
(function () {
    // document.currentScript is null in a deferred script, so find our own tag.
    const script = document.querySelector('script[src$="javascript/commonHeader.js"]');
    const root = ((script && script.src) || '').replace(/javascript\/commonHeader\.js.*$/, '') || './';

    function has(selector) {
        return document.head.querySelector(selector) !== null;
    }

    function add(tag, attrs) {
        const el = document.createElement(tag);
        for (const key in attrs) el.setAttribute(key, attrs[key]);
        document.head.appendChild(el);
    }

    if (!has('link[rel="icon"]')) {
        add('link', { rel: 'icon', type: 'image/svg+xml', href: root + 'img/icon/favicon.svg' });
    }

    if (!has('link[rel="stylesheet"][href$="style/base.css"]')) {
        add('link', { rel: 'stylesheet', href: root + 'style/base.css' });
    }

    const og = {
        'og:title': "Stefano Costa's Webpage",
        'og:description': "Stefano Costa's personal website, featuring his scientific research, publications, and projects",
        'og:image': 'https://stefanocosta.me/img/preview_image.jpg',
        'og:url': 'https://stefanocosta.me/',
        'og:type': 'website'
    };
    for (const property in og) {
        if (!has('meta[property="' + property + '"]')) {
            add('meta', { property: property, content: og[property] });
        }
    }
})();
