# artelle

Artist portfolio & shop-front for **Artelle** — artelle.xyz.

Static site (plain HTML/CSS/JS, no build step). Deploys on Render as a Static Site.
Publish directory: `.` (repo root). No build command.

## Pages

| Page | What |
|---|---|
| `index.html` | Hero, selected works, statement, "three ways to own" |
| `works.html` | Full catalogue + filters + lightbox |
| `editions.html` | Original vs archival print vs digital edition, how buying works |
| `about.html` | Statement, bio, commissions |
| `contact.html` | Email / Instagram / studio visits / list |

## Brand

- Mark: **Horizon** (dot at rest on a line) — `assets/img/logo.svg`, reverse `logo-reverse.svg`, `favicon.svg`
- Six explored directions live in `assets/brand/concepts/`; the proof sheet is `design/marks.html`
- Palette: paper `#F4F1E9`, ink `#1C1712`, secondary `#6B6353`, hairline `#DCD5C5`, ultramarine accent `#33439B`
- Type: Cormorant Garamond (display) + Instrument Sans (text), Google Fonts

## ⚠️ Placeholders to replace before announcing

Everything below is stand-in copy/art so the site reads finished:

1. **All artwork** — `assets/art/study-*.svg` are generated placeholder studies.
   Replace with photos/scans of real work (JPG/WebP ~2000px long edge), then update
   `src`, `alt`, titles, medium, sizes, and prices in `index.html` + `works.html`.
   Keep the `data-cats` attribute (`original print edition`) per availability.
2. **Artist name/bio** — site uses "Artelle" as the artist name; swap in her name
   and real statement in `about.html` (+ hero line in `index.html`).
3. **Email** — `hello@artelle.xyz` needs a mailbox or forward set up.
4. **Instagram** — currently links to `instagram.com/artelle` (may be taken).
5. **Prices** — invented; set real ones.
6. **CV** — placeholder rows in `about.html`.
7. **OG image** — add `assets/img/og.jpg` + `<meta property="og:image">` once real art exists.

## Deploy (Render)

1. Render dashboard → **New → Static Site** → connect `syedos/artelle`.
2. Build command: *(none)* · Publish directory: `.`
3. Custom domains: add `artelle.xyz` and `www.artelle.xyz`, then at the DNS
   provider point the apex A record to Render's load balancer IP and `www`
   CNAME to the `onrender.com` URL (Render shows both values on the domain page).

## Local check

No dev server needed — open any page directly, or `python3 -m http.server` if you
want clean relative paths. Push to `main` = deployed.
