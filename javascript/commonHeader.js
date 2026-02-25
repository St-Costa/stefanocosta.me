(function () {
    // Use insertBefore(el, script) so that the inserted elements appear BEFORE
    // the inline <link> tags in the HTML, guaranteeing correct CSS cascade order.
    const script = document.currentScript;
    const path = window.location.pathname;
    const folder = (path.endsWith("index.html") || path.endsWith("/")) ? "./style/" : "../style/";

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

    addMeta({ charset: "UTF-8" });
    addMeta({ name: "viewport", content: "width=device-width, initial-scale=1.0" });

    addStylesheet(folder + "night_mode.css");
    addStylesheet(folder + "styling.css");
    addStylesheet(folder + "footer.css");
    addStylesheet(folder + "phone.css");

    addMeta({ property: "og:title", content: "Stefano Costa's Webpage" });
    addMeta({ property: "og:description", content: "Stefano Costa's personal website, featuring his scientific research, publications, and projects" });
    addMeta({ property: "og:image", content: "https://st-costa.github.io//img/preview_image.jpg" });
    addMeta({ property: "og:url", content: "https://st-costa.github.io/" });
})();
