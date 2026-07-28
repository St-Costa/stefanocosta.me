# stefanocosta.me

**Live:** [stefanocosta.me](https://stefanocosta.me) · **Blog:** [Source of Truth](https://stefanocosta.me/mainPages/Blog_pages.html) · [RSS](https://stefanocosta.me/mainPages/blogFeed.xml)

<p align="center">
  <img src="img/readme/homepage.webp" alt="The site's homepage: a centred monospace index on a dark background" width="60%">
</p>

---

## Design choices

### Plain HTML, CSS and a little JavaScript

I don't like websites that are complicated to read or to maintain.

So this one has no framework, no bundler and no build step: just HTML, CSS and a little
JavaScript — about a thousand lines of the two combined.

### No tracker

The site sets **no cookies** and runs **no analytics and no trackers**:
- **No Google Fonts**: [JetBrains Mono](https://www.jetbrains.com/lp/mono/) is self-hosted,
  subset down to the ~120 characters the site actually uses.
- **No icon CDN**: the handful of icons are inline SVG.
- **No hotlinked images**: book covers, podcast artwork and screenshots of tweets are stored
  in this repository instead of loaded from Amazon, Apple or X. They still link back to
  wherever they came from.

Every page loads from one origin: mine. Nobody else gets to see who visits.

### Performance

Because there is so little to load, the site scores 100 across the board on
[PageSpeed Insights](https://pagespeed.web.dev/analysis/https-stefanocosta-me/wvalfrpn59?form_factor=desktop).

<p align="center">
  <img src="img/readme/lighthouse-mobile.webp" alt="PageSpeed Insights, mobile: Performance, Accessibility, Best Practices and SEO all 100" width="49%">
  <img src="img/readme/lighthouse-desktop.webp" alt="PageSpeed Insights, desktop: Performance, Accessibility, Best Practices and SEO all 100" width="49%">
</p>

<p align="center"><em>Mobile · desktop</em></p>
