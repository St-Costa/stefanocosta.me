document.addEventListener("DOMContentLoaded", function() {
    const tocContainer = document.querySelector(".toc");
    if (!tocContainer) return; // No TOC element on this page

    const headers = document.querySelectorAll("h2, h3, h4");

    let tocHTML = "";

    headers.forEach((header, index) => {
        // Skip the first 2 headers (H1 title + subtitle rendered as H2/H3)
        if (index < 2) return;
        if (header.textContent == "TL;DR") return // Skip TL;DR
        if (header.textContent == "TOC") return // Skip TOC
        // Skip h4 inside callouts (e.g. callout titles)
        if (header.tagName === "H4" && header.closest(".callout")) return;

        header_string = header.textContent.trim();

        header_string = header_string.replace("■", "");
        header_string = header_string.replace("└─", "");
        header_string = header_string.replace("├─", "");

        const nextElement = headers[index + 1];
        let level;
        if (header.tagName === "H2") {
            level = "■";
        } else if (header.tagName === "H4") {
            const nextIsH4 = nextElement && nextElement.tagName === "H4" && !nextElement.closest(".callout");
            level = nextIsH4 ? "&nbsp;&nbsp;&nbsp;├─" : "&nbsp;&nbsp;&nbsp;└─";
        } else {
            level = (nextElement && nextElement.tagName !== "H2") ? "├─" : "└─";
        }
        const link = `<a href="#${header.id}">${header_string}</a>`;
        tocHTML += `${level} ${link}<br>`;
        if (nextElement && nextElement.tagName === "H2") {
            tocHTML += "<div style='height:3ch; display:inline-block;'></div>";
        }
    });

    const scrollDiv = document.createElement('div');
    scrollDiv.className = 'toc-scroll';
    scrollDiv.innerHTML = tocHTML;
    tocContainer.appendChild(scrollDiv);
});
