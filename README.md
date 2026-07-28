# stefanocosta.me

**Live:** [stefanocosta.me](https://stefanocosta.me) · **Blog:** [Source of Truth](https://stefanocosta.me/mainPages/Blog_pages.html) · [RSS](https://stefanocosta.me/mainPages/blogFeed.xml)

<p align="center">
  <img src="img/readme/homepage.webp" alt="The site's homepage: a centred monospace index on a dark background" width="60%">
</p>

---

## Design choices

### Plain HTML, CSS and a little JavaScript

I don't like websites that are complicated — complicated to read, and complicated to keep
alive. So this one has no framework, no bundler, no `node_modules` and no build step: every
page is hand-written HTML served straight off GitHub Pages, and the repository *is* what
ships.

The whole site is under 1,000 lines of CSS and JavaScript. That is a constraint I picked on
purpose, and it buys two things:

- **It stays simple to maintain.** There is no toolchain to upgrade and nothing that breaks
  because an upstream package cut a major version. `git clone` and open a file — that's the
  entire setup.
- **It stays fast.** No runtime, no hydration, no framework to download before anything
  appears on screen.

JavaScript is used where it genuinely removes work — building a post's table of contents from
its headings, rendering the footer — and nowhere else. Nothing on the page depends on it to
be readable.

### Nothing that follows you around

This is the part I care about most. The site sets **no cookies** — so there is no consent
banner to dismiss — and runs **no analytics and no trackers**. I don't count you, profile
you, or hand you to anyone who would.

Getting there meant refusing the conveniences that quietly leak visitors to other companies:

- **No Google Fonts.** JetBrains Mono is self-hosted, subset down to the ~120 characters the
  site actually uses. Loading it from Google's servers would send every visitor's IP address
  to Google in exchange for some nice typography.
- **No icon CDN.** The handful of icons are inline SVG rather than a 75 KB webfont fetched
  from a third party.
- **No comment platform, no share buttons, no video players.** The usual vehicles for
  third-party cookies simply aren't here.

The result: **every page makes zero third-party requests.** Book and podcast covers are hosted
here rather than hotlinked from Amazon and Apple, and quoted tweets are local screenshots that
link back to the original — an embed is a third-party script that can set cookies, and it
leaves a blank gap for anyone running a blocker. Each screenshot carries the tweet's full
wording in its `alt` text, so the quote is still there for a screen reader.

Following the blog works the same way: the [RSS feed](https://stefanocosta.me/mainPages/blogFeed.xml)
is generated from the posts themselves, so reading it doesn't require an account anywhere.

### Performance as a consequence, not a project

Because there is so little to load, the site scores 100 across the board on
[PageSpeed Insights](https://pagespeed.web.dev/analysis/https-stefanocosta-me/wvalfrpn59?form_factor=desktop) —
on desktop with a Largest Contentful Paint of 0.3 s and zero layout shift.

<p align="center">
  <img src="img/readme/lighthouse-mobile.webp" alt="PageSpeed Insights, mobile: Performance, Accessibility, Best Practices and SEO all 100" width="49%">
  <img src="img/readme/lighthouse-desktop.webp" alt="PageSpeed Insights, desktop: Performance, Accessibility, Best Practices and SEO all 100" width="49%">
</p>

<p align="center"><em>Mobile · desktop</em></p>

Getting there still took deliberate work — being static does not make a site fast on its own.
Every image declares its real dimensions so the layout never jumps while they load, the
critical fonts are preloaded, the stylesheet is inlined on the homepage where a first-time
visitor has an empty cache, and the one script the site uses is deferred so it cannot delay
the first paint.
