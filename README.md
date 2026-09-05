# Artelle

Original artwork by **Anisa Quraishi**, an artist based in Pakistan.

[artelle.xyz](https://artelle.xyz) is a static HTML/CSS/JS site hosted on **Render,
syedOS workspace**. GitHub is `artellexyz/artelle`, managed through **buxor**.
No Robomart hosting, database or payment resources are used.

## Catalog

`catalog/artworks.json` is the editable master: one stable `AQ-0001` style ID
per original. It currently contains **34 artworks**. Proposed titles, exact
reverse inscriptions, photo references, date evidence and review flags are
preserved alongside public metadata. Prices and availability are unconfirmed.

The September 2026 import has 62 photos: **31 fronts, 30 matching reverses and
one extra reverse view**. Seventeen fronts match previous catalog entries;
fourteen are new. Three previous works (AQ-0001, AQ-0013, AQ-0020) are retained
without corresponding photos in the new batch.

The sequence is generally **reverse, then front**. IMG_2508 has no supplied
reverse. IMG_2541 is an extra view of the reverse shown clearly in IMG_2542.
Only the top sheet's inscription belongs to the next front; captions on
underlying sheets must not be copied onto it.

`catalog/imports/2026-09-06.json` accounts for every photograph with a role,
artwork ID and SHA-256 digest. Full photographs and untouched HEIC originals
are archived locally under `~/Documents/Artelle/archive/2026-09-06/`.

## Generate and verify

Python 3's standard library is sufficient for normal catalog updates:

```sh
python3 scripts/build_catalog.py
python3 scripts/build_catalog.py --check
node --check assets/js/site.js
```

This generates the gallery, home/about/contact/collecting pages, a searchable
catalog table, 34 individual artwork pages, a public CSV, sitemap and robots file.
All catalog content is present in the initial HTML and works without JavaScript.
JavaScript adds filters, table search and an accessible lightbox.

The public spreadsheet contains artwork metadata. Source matching and review
flags are included in the richer local spreadsheet and SQLite snapshot:

```sh
python3 scripts/build_catalog.py \
  --exports "$HOME/Documents/Artelle" \
  --archive "$HOME/Documents/Artelle/archive/2026-09-06"
```

This writes `artworks.csv`, `artworks.json`, `artelle.sqlite` and `review.html`
outside the repository. SQLite has `artworks` and `photos` tables, with a foreign
key between them. These are **generated snapshots**, not a second editable
master; rebuilding replaces them. Keep future sales and customer records in a
separate private store.

## Images

The 20 existing clean images are retained. Fourteen new fronts are cropped and
straightened using the recorded quadrilaterals in
`catalog/imports/2026-09-06-crops.json`. Colour is converted to sRGB; public
images omit source EXIF metadata. No paint is generated or reconstructed.
Three abstracts are rotated to put the artist's signature upright.

To regenerate web images and thumbnails, use a Python with Pillow installed:

```sh
python3 scripts/prepare_images.py \
  --archive "$HOME/Documents/Artelle/archive/2026-09-06"
python3 scripts/build_catalog.py
```

On the current Mac, the Pillow installation is arm64; use `arch -arm64 python3`
for the image preparation command. Normal catalog builds work with either
architecture. Image preparation is an offline task, not a Render dependency.

## Details still to confirm

- Four media, seven dimensions and nine years remain unconfirmed.
- AQ-0024 (Verdure) has **2018 on the front and 2017 on the reverse**. Its year
  stays blank until the artist resolves the conflict.
- Twelve newly photographed works need a front photo without hands; two of
  these also need the paper laid flat. The local review shows every front/back
  pair and its flags.
- All titles are proposals. Prices, availability, framing and shipping details
  have not been supplied.
- Dimensions follow the handwritten inches, normalized to height × width for
  display. Whether they describe the entire sheet or the painted area is not
  specified. Centimeters are converted mathematically.
- The existing `hello@artelle.xyz` contact address is retained; mailbox delivery
  has not been verified. The unverified Instagram link was removed.
- No checkout, print fulfillment or digital-edition service is configured.
  Collecting pages therefore use enquiries and make no fulfillment promises.

## Deployment

Render service: `srv-da4uu6m417fc73dle3lg`, workspace **syedOS**.
Origin: `https://artelle-pi2e.onrender.com`.
Domains: `artelle.xyz` and `www.artelle.xyz`.

Build command is blank; publish directory is `.`. Generated outputs are committed
alongside the master, so Render needs no runtime, database or image-processing
packages. Push to `main`, then confirm Render deployed that exact commit and
verify the public site. Use `GITHUB_TOKEN_BUXOR` for GitHub and
`RENDER_API_KEY_SYEDOS` for Render.
