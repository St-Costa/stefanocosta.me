<p align="center">
  <img src="img/icon/favicon.svg" alt="" width="120">
</p>

<h1 align="center">stefanocosta.me</h1>

<p align="center">
  <em>A personal site and blog</em>
</p>

<p align="center">
  <img alt="HTML" src="https://img.shields.io/badge/HTML-hand--written-E34F26?logo=html5&logoColor=white">
  <img alt="CSS" src="https://img.shields.io/badge/CSS-no%20framework-1572B6?logo=css3&logoColor=white">
  <img alt="JavaScript" src="https://img.shields.io/badge/JavaScript-vanilla-F7DF1E?logo=javascript&logoColor=black">
  <img alt="Build step" src="https://img.shields.io/badge/build%20step-none-2ea44f">
  <img alt="Dependencies" src="https://img.shields.io/badge/dependencies-0-2ea44f">
  <img alt="Trackers" src="https://img.shields.io/badge/trackers-0-2ea44f">
</p>

<p align="center">
  <sub>…yes, those badges are the only third-party images in this repository.</sub>
</p>

<p align="center">
  <strong>Live:</strong> <a href="https://stefanocosta.me">stefanocosta.me</a> ·
  <strong>Blog:</strong> <a href="https://stefanocosta.me/mainPages/Blog_pages.html">Source of Truth</a> ·
  <a href="https://stefanocosta.me/mainPages/blogFeed.xml">RSS</a>
</p>

<p align="center">
  <img src="img/readme/homepage.webp" alt="The site's homepage: a centred monospace index on a dark background" width="60%">
</p>

---

## Design choices

### Plain HTML, CSS and a little JavaScript

I don't like websites that are complicated to read or to maintain.

So this one has no framework, no bundler and no build step: just HTML, CSS and a little
JavaScript.

### No tracker

The site sets **no cookies** and runs **no analytics and no trackers**:
- **No Google Fonts**: [JetBrains Mono](https://www.jetbrains.com/lp/mono/) is self-hosted,
  subset down to the ~120 characters the site actually uses.
- **No icon CDN**: the handful of icons are inline SVG.
- **No hotlinked images**: they are stored in the repo, still linking back to the source.

### Performance

The site scores 100 across the board on
[PageSpeed Insights](https://pagespeed.web.dev/analysis/https-stefanocosta-me/wvalfrpn59?form_factor=desktop).

<p align="center">
  <img src="img/readme/lighthouse-mobile.webp" alt="PageSpeed Insights, mobile: Performance, Accessibility, Best Practices and SEO all 100" width="49%">
  <img src="img/readme/lighthouse-desktop.webp" alt="PageSpeed Insights, desktop: Performance, Accessibility, Best Practices and SEO all 100" width="49%">
</p>

<p align="center"><em>Mobile · desktop</em></p>
