(function () {
    // Use insertBefore(el, script) so that the inserted elements appear BEFORE
    // the inline <link> tags in the HTML, guaranteeing correct CSS cascade order.
    const script = document.currentScript;
    const root = ((script && script.src) || '').replace(/javascript\/commonHeader\.js.*$/, '') || './';
    const folder = root + 'style/';

    function addLink(attrs) {
        const link = document.createElement("link");
        for (const key in attrs) {
            link.setAttribute(key, attrs[key]);
        }
        insert(link);
    }

    function insert(el) {
        if (script && script.parentNode) {
            script.parentNode.insertBefore(el, script);
        } else {
            document.head.appendChild(el);
        }
    }

    function addMeta(attrs) {
        const meta = document.createElement("meta");
        for (const key in attrs) {
            meta.setAttribute(key, attrs[key]);
        }
        insert(meta);
    }

    function addStylesheet(href) {
        const link = document.createElement("link");
        link.rel = "stylesheet";
        link.href = href;
        insert(link);
    }

    const imgFolder = root + 'img/';
    addLink({ rel: "icon", type: "image/svg+xml", href: imgFolder + "icon/favicon.svg" });
    addStylesheet(folder + "base.css");

    const d = script ? script.dataset : {};
    addMeta({ property: "og:title",       content: d.ogTitle       || "Stefano Costa's Webpage" });
    addMeta({ property: "og:description", content: d.ogDescription || "Stefano Costa's personal website, featuring his scientific research, publications, and projects" });
    addMeta({ property: "og:image",       content: d.ogImage       || "https://st-costa.github.io/img/preview_image.jpg" });
    addMeta({ property: "og:url",         content: d.ogUrl         || "https://st-costa.github.io/" });
    addMeta({ property: "og:type",        content: d.ogType        || "website" });
})();
