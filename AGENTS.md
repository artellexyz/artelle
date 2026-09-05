# Artelle

- Artelle is independent of Robomart. Do not use Robomart accounts, credits, databases or credentials.
- GitHub: `artellexyz/artelle`, managed with `GITHUB_TOKEN_BUXOR`. Commit as the buxor identity and push to `main`.
- Hosting: existing Render static site `artelle`, service `srv-da4uu6m417fc73dle3lg`, in the syedOS workspace. Use `RENDER_API_KEY_SYEDOS` only. Verify the deployed commit and public pages after a push.
- `catalog/artworks.json` is the editable master. Run `python3 scripts/build_catalog.py` after changes, and `python3 scripts/build_catalog.py --check` before committing. HTML and CSV are generated outputs.
- Read the photo manifest and inscriptions before changing a match. The September import generally puts the reverse BEFORE its matching front, with an extra reverse photo at IMG_2541.
- Preserve unknown and conflicting details. Never infer medium, physical dimensions, availability or price from appearance or neighbouring artworks.
- Preserve the original artwork. Crop, straighten and convert colour profiles for display; do not synthesize covered or missing paint.
- This repository and its deployment are public. Original HEICs, complete reverse photos, customer details, payment records and private SQLite exports belong outside the repository.
