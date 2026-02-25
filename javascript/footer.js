(function () {
    const path = window.location.pathname;
    const inBlogPosts = path.includes('/blogPosts/');
    const inMainPages = path.includes('/mainPages/');

    const colophonHref = inMainPages ? "./colophon.html" : "../mainPages/colophon.html";
    const blogHref = inBlogPosts ? "../mainPages/Blog_pages.html" : null;

    const footer = document.createElement("footer");
    let html = `<a href="../index.html">Home</a>&nbsp;&nbsp;`;
    if (blogHref) {
        html += `<a href="${blogHref}">Blog</a>&nbsp;&nbsp;`;
    }
    html += `<a href="${colophonHref}">Colophon</a>`;
    footer.innerHTML = html;
    document.body.appendChild(footer);

    // Buttons that open a URL in a new tab
    document.querySelectorAll("button[data-href]").forEach(function (btn) {
        btn.addEventListener("click", function () {
            window.open(btn.getAttribute("data-href"));
        });
    });

    // Buttons that navigate in the same tab
    document.querySelectorAll("button[data-location]").forEach(function (btn) {
        btn.addEventListener("click", function () {
            window.location.href = btn.getAttribute("data-location");
        });
    });
})();
