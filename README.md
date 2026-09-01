# artelle

Artist portfolio & shop-front for **Artelle** — artelle.xyz.

Static site (plain HTML/CSS/JS, no build step). Deploys on Render as a Static Site.
Publish directory: `.` (repo root). No build command.

## Pages

| Page | What |
|---|---|
| `index.html` | Hero, selected works, formats band |
| `works.html` | Full catalogue (20 works) + lightbox |
| `editions.html` | Original vs archival print vs digital edition, how buying works |
| `about.html` | Bio, commissions |
| `contact.html` | Email / Instagram / studio visits / list |

## Catalogue

20 works live in `assets/art/work-01.jpg … work-20.jpg` (resized to ≤1600px long edge,
JPEG q85, via `sips`). To add a piece: drop the JPG in `assets/art/`, add a card in
`works.html` (and optionally `index.html`). Captions are title + medium only; buying
is enquire-by-email.

## Brand

- Mark: **Horizon** (dot at rest on a line) — `assets/img/logo.svg`, reverse `logo-reverse.svg`, `favicon.svg`
- Six explored directions live in `assets/brand/concepts/`; the proof sheet is `design/marks.html`
- Palette: paper `#F4F1E9`, ink `#1C1712`, secondary `#6B6353`, hairline `#DCD5C5`, ultramarine accent `#33439B`
- Type: Cormorant Garamond (display) + Instrument Sans (text), Google Fonts

## ⚠️ Placeholders to replace before announcing

1. **Titles / prices** — titles are descriptive (set by the studio, not the artist yet); everything is "enquire".
2. **Email** — `hello@artelle.xyz` needs a mailbox or forward set up.
3. **Instagram** — currently links to `instagram.com/artelle` (may be taken).
4. **CV** — minimal rows in `about.html`.

## Deploy (Render)

1. Render dashboard → **New → Static Site** → connect `syedos/artelle`.
2. Build command: *(none)* · Publish directory: `.`
3. Custom domains: add `artelle.xyz` and `www.artelle.xyz`, then at the DNS
   provider point the apex A record to Render's load balancer IP and `www`
   CNAME to the `onrender.com` URL (Render shows both values on the domain page).

## Local check

No dev server needed — open any page directly, or `python3 -m http.server` if you
want clean relative paths. Push to `main` = deployed.
