# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Portfolio and shop-front for **Artelle**, a watercolor / colored-pencil / pastel artist (South Asian architecture, blossoms, florals). Live at **https://artelle.xyz** (Render static site, also https://artelle-pi2e.onrender.com). Audience: print buyers first, digital-edition collectors second. Buying is enquire-by-email; there is no cart.

Plain HTML/CSS/JS. **No build step, no package.json, no tests, no linter.** There is nothing to install or run. Push to `main` = deployed (Render autodeploys). Do not start a local server; open the HTML files directly if a visual check is needed.

## Commands

The only command this repo needs is the image-prep recipe for new artwork (≤1600px long edge, JPEG q85, via macOS `sips`):

```
sips -Z 1600 -s format jpeg -s formatOptions 85 source.jpg --out assets/art/work-NN.jpg
```

## Architecture

**Five standalone pages, no templating.** `index.html`, `works.html`, `editions.html`, `about.html`, `contact.html` each carry a full copy of the `<head>` (Google Fonts link, meta), the header (brand + nav), and the footer. The header block is byte-identical across all five. Any change to nav, footer, fonts, or the inline brand mark must be applied to every page. Each page marks its own nav link with `aria-current="page"`.

**Shared assets:** `assets/css/site.css` (all tokens in `:root`, sections marked with `/* ---------- name ---------- */` comments) and `assets/js/site.js` (one IIFE: scroll reveal, category filters, lightbox).

**Work-card contract.** The lightbox depends on this exact shape, so every card must follow it:

```html
<a class="work reveal" href="assets/art/work-NN.jpg" data-title="Title" data-meta="Medium on paper">
  <figure>
    <div class="plate"><img src="assets/art/work-NN.jpg" alt="..." loading="lazy"></div>
    <figcaption class="cap"><div><div class="title">Title</div><div class="meta">Medium on paper</div></div></figcaption>
  </figure>
</a>
```

`site.js` intercepts clicks on `a.work`, copies the `.plate` innerHTML into `#lightbox .lb-frame`, and reads `data-title` / `data-meta` for the caption. Prev/next cycle through non-hidden `.work` elements in DOM order. The `<div class="lb" id="lightbox">` block lives only on `index.html` and `works.html`; a page with cards but no lightbox falls back to the plain `href`.

**Catalogue.** `assets/art/work-01.jpg … work-20.jpg`. `works.html` shows all 20; `index.html` shows a hero piece (work-01, Mosque) plus 6 selected cards. To add a piece: drop the resized JPG in `assets/art/`, add a card to `works.html`, optionally to `index.html`. Captions are title + medium only; no prices on the site.

**Dormant filter code.** `site.js` supports `.chip[data-filter]` buttons toggling `.work[data-cats]` cards, but no page currently renders chips or `data-cats`. It is safe to remove or to wire up.

**Brand.** Mark is **Horizon** (dot resting on a line). It exists as files (`assets/img/logo.svg`, `logo-reverse.svg`, `favicon.svg`) but the header and footer embed it as inline SVG, so a mark change means editing the inline SVGs on all pages too. Palette: paper `#F4F1E9`, raise `#FBF9F3`, ink `#1C1712`, ink-2 `#6B6353`, line `#DCD5C5`, accent ultramarine `#33439B`. Type: Cormorant Garamond (display, italic titles) + Instrument Sans (text). The six rejected mark concepts and the proof sheet (`assets/brand/concepts/`, `design/marks.html`) are reference only; the proof sheet has its own inline CSS and is not linked from the site.

**Voice.** Copy is plain portfolio prose matched to representational work. Do not drift back toward abstract or conceptual-art language.

## Deploy and identity

- **GitHub:** `artellexyz/artelle`. This is a **buxor-family identity**. Push with `GITHUB_TOKEN_BUXOR`. The macOS keychain injects cached roboalias credentials over any supplied token, so push like this (the empty helper first resets the chain):
  ```
  git -c credential.helper= -c credential.helper='!f(){ echo username=buxor; echo password=$GITHUB_TOKEN_BUXOR; };f' push origin main
  ```
- **Render:** syedos account (`RENDER_API_KEY_SYEDOS`), service `artelle` (`srv-da4uu6m417fc73dle3lg`), publish path `.`, no build command, autoDeploy on.
- **Repo must stay PUBLIC.** If made private, the syedos Render GitHub App loses access and deploys fail. To go private, grant Render's GitHub App on the `artellexyz` org first.
- **DNS** is at Porkbun. The Porkbun API has been WAF-blocked from this machine and our cloud boxes; DNS edits go through the browser. Records: apex A → `216.24.57.1`, `www` CNAME → `artelle-pi2e.onrender.com`.
- **Gotcha:** `og:image` on `index.html` and `works.html` still points at the `onrender.com` hostname. Switch to `https://artelle.xyz/...` now that the domain resolves.

## Open placeholders

Still unresolved as of Sep 2026: `hello@artelle.xyz` has no mailbox or forward; the Instagram link (`instagram.com/artelle`) is unverified; `about.html` CV rows are minimal; titles were set by the studio, not the artist; no prices anywhere. Do not invent any of these.
