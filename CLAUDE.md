# CLAUDE.md

Guidance for this repository. Read `AGENTS.md` and `README.md` for the catalog
workflow, photo matching evidence and current gaps.

## What this is

Artelle is the portfolio of **Anisa Quraishi**, an artist based in Pakistan.
Live at **https://artelle.xyz**, on the existing Render static site in **syedOS**.
Use **buxor** for GitHub. Never use Robomart accounts, credentials or credits.

The catalog has **34 artworks**. There is no cart or payment service. Sales
are not open yet: the old `hello@artelle.xyz` address has no configured mail
records. `CONTACT_EMAIL` in `scripts/build_catalog.py` remains `None` until
the studio supplies a working address. Public pages show enquiries opening soon.

## Source and commands

`catalog/artworks.json` is the editable master. Never hand-edit generated
pages or CSV. Use the standard-library Python generator:

```sh
python3 scripts/build_catalog.py
python3 scripts/build_catalog.py --check
node --check assets/js/site.js
```

`templates/page.html` supplies the shared page structure; `assets/css/site.css`
and `assets/js/site.js` supply presentation and progressive enhancement. All
catalog content is available without JavaScript. The generator creates six
main pages, 34 artwork detail pages, a public CSV, sitemap and robots file.
There is no runtime or package installation. Do not start a localhost server.
Verify the deployed site using the Superset browser.

Normal artwork updates happen in the master, followed by a rebuild. Preserve
unknowns, date conflicts, proposed-title status and source-photo mappings.
Full reverse photographs, HEIC originals and local SQLite exports stay outside
this public repository. See `README.md` for archive and export commands.

For new photographs, use the documented crop recipes and
`scripts/prepare_images.py`; do not generate or reconstruct covered artwork.
On this Mac, Pillow needs `arch -arm64 python3`.

## Gallery behavior

Artwork cards link to `work/aq-NNNN.html`. Their `data-image` points to the
full-resolution display photo; their embedded image is a thumbnail.
`site.js` adds category filtering, catalog search and a lightbox with details,
previous/next controls, focus restoration and keyboard navigation. A page
without JavaScript follows the artwork detail links normally.

## Brand and voice

**Brand.** Mark is **Horizon** (dot resting on a line). It exists as files (`assets/img/logo.svg`, `logo-reverse.svg`, `favicon.svg`) and the shared header embeds it as inline SVG in `templates/page.html`. Change the template and rebuild when adopting a new mark. Palette: paper `#F4F1E9`, raise `#FBF9F3`, ink `#1C1712`, ink-2 `#6B6353`, line `#DCD5C5`, accent ultramarine `#33439B`. Type: Cormorant Garamond (display, italic titles) + Instrument Sans (text). The six rejected mark concepts and the proof sheet (`assets/brand/concepts/`, `design/marks.html`) are reference only; the proof sheet has its own inline CSS and is not linked from the site.

**Pixel A mark (Sheet 2, Sep 2026).** `design/pixel-a.py` is the single source: it holds 32×32 ASCII grids for two letterforms (italic capital A, cursive a) and four flowers (rose, tulip, blossom, bud), and emits `assets/brand/pixel/*.svg` (ink / ultra / colour / reverse per mark) plus the proof page `design/pixel-a.html`. Edit the grids in the script and rerun it; never hand-edit those SVGs or the HTML. `--png /tmp/px` also writes PNG previews and a contact sheet for eyeballing. Not yet adopted as the site mark; the header still uses Horizon.

**Voice.** Use plain portfolio prose. Describe the actual artwork without inventing biography, artistic intent, exhibitions or sales promises.

## Deploy and identity

- **GitHub:** `artellexyz/artelle`. This is a **buxor-family identity**. Push with `GITHUB_TOKEN_BUXOR`. The macOS keychain injects cached roboalias credentials over any supplied token, so push like this (the empty helper first resets the chain):
  ```
  git -c credential.helper= -c credential.helper='!f(){ echo username=buxor; echo password=$GITHUB_TOKEN_BUXOR; };f' push origin main
  ```
- **Render:** syedos account (`RENDER_API_KEY_SYEDOS`), service `artelle` (`srv-da4uu6m417fc73dle3lg`), publish path `.`, no build command, autoDeploy on, but verify the deployed commit: the September catalog required an explicit deploy through the syedOS Render API.
- **Repo must stay PUBLIC.** If made private, the syedos Render GitHub App loses access and deploys fail. To go private, grant Render's GitHub App on the `artellexyz` org first.
- **DNS** is at Porkbun. The Porkbun API has been WAF-blocked from this machine and our cloud boxes; DNS edits go through the browser. Records: apex A → `216.24.57.1`, `www` CNAME → `artelle-pi2e.onrender.com`.

## Unconfirmed information

Prices, availability, framing and shipping are unconfirmed. Four media,
seven dimensions and nine years are missing or conflicting. All titles are
proposals. Twelve uploaded front photos need retakes without hands. See the
private review report and catalog flags; do not invent missing details.
