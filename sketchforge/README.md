# SketchForge

Turns a customer photo into

1. a **realistic pencil sketch** or a **clean outline to trace**, and
2. an **SVG paint-by-numbers** where you choose the number of colours.

There is no generative AI in it. It uses classical computer vision and maths (filters, edge detection,
k-means colour clustering, geometry), so **the same photo with the same settings gives the same
result every time, down to the byte.** That is the point: AI image tools redraw the photo and change
on every run, this does not.

```
sketchforge/
├── backend/    Python · FastAPI · OpenCV / NumPy / SciPy   (the engine + HTTP API + CLI)
├── frontend/   Next.js 14 · React · TypeScript              (the web app)
├── samples/    two test photos + example outputs and their recipes
└── run.sh      starts both servers (bash run.sh)
```

## Run it

You need Python 3.10+ and Node 18+.

```bash
# 1. backend (terminal 1)
cd backend
python3 -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --port 8000

# 2. frontend (terminal 2)
cd frontend
npm install
npm run dev                                              # http://localhost:3000
```

`bash run.sh` does both on macOS / Linux (creates the virtualenv and installs packages the first time). If the backend runs somewhere else, copy
`frontend/.env.local.example` to `frontend/.env.local` and set `NEXT_PUBLIC_API_URL`.
When serving the frontend from another origin, set `ALLOWED_ORIGINS` (comma separated) for the backend.

## Using it

1. Drop in a photo.
2. Pick **Sketch / trace** or **Paint by numbers**, optionally start from a preset.
3. Move the sliders; the preview updates by itself (a fast 720px render).
4. Download. Downloads are rendered at full resolution and tagged for the print size you set.

**Sketch styles**

| Style | What it is | Best for |
|---|---|---|
| Pencil | Colour-dodge pencil drawing with soft graphite shading and paper grain | Realistic portraits, pets |
| Outline | XDoG line art, thickness and sensitivity adjustable | Tracing onto canvas |
| Hatch | Pen-style hatching that follows the shape of the subject, 2–8 layers | Stylised drawings |
| Tones | A 2–8 level value map | Showing where darks and lights go before painting |

Extras: **draw a detail box** over a face to render that area with more detail, a **transfer grid**
overlay, cream or white paper, and a print width in cm (the PNG carries the matching DPI).

**Paint-by-numbers**

| Setting | Effect |
|---|---|
| Number of colours | 2–48 colours, chosen in CIELAB (perceptual) colour space |
| Smallest shape (mm) | Every shape can hold a circle this wide at the chosen print size. Anything smaller is merged into its closest-coloured neighbour, so every shape fits a brush and a number |
| Smooth out texture / Tidy edges / Curve smoothness | Control how clean and simple the shapes are |
| Colour 1 | Always the darkest colour; numbers run dark → light |

SVG downloads: **canvas** (white shapes, outlines, numbers, colour key: the sheet to print and paint),
**guide** (coloured shapes + numbers), **painted** (coloured preview, no lines). They open in Inkscape,
Illustrator, Affinity or a browser. Layers have stable ids (`fills`, `outlines`, `numbers`, `legend`, `color-N`).
The SVG is sized in cm, so it prints at the width you chose.

### Same input, same output

Every render has a **fingerprint** (SHA-256 of the output). The **recipe** download is a small JSON
file with all settings plus the fingerprint of the photo. Load it again later (button **Load settings**, or
the CLI) with the same photo and you get the identical file. Randomness (paper grain, hand wobble,
k-means starting points) comes only from a `seed` setting (default 7).

## How it works

**Sketch** (`backend/app/engine/sketch.py`)
- *Pencil*: CLAHE local contrast → Gaussian blur of the inverted image → colour-dodge divide, blended with a
  little real tone for shading, then seeded graphite grain.
- *Outline*: bilateral filter (keeps contours, removes texture) → extended difference of Gaussians (XDoG)
  with a soft threshold → speck removal → morphological thickening.
- *Hatch*: structure tensor gives the direction of contours; each tone layer draws anti-aliased stripe
  patterns along (or across) that direction, with seeded low-frequency wobble.
- *Tones*: edge-preserving smoothing → quantile cut points → median clean-up.
- Sizes scale with the image (1000px = 1×), so a 720px preview and a 3000px export look alike.

**Paint-by-numbers** (`pbn.py`, `vectorize.py`, `svgout.py`)
1. Bilateral smoothing, then seeded k-means++ in Lab (own implementation, fixed iteration order).
2. Majority filter, then 4-connected regions.
3. One global distance transform measures every region's inscribed radius; regions smaller than the
   minimum are merged into their closest-colour neighbour (repeated until none are left).
4. **Shared-edge tracing**: boundaries are traced once, on the pixel cracks, between junctions, smoothed,
   simplified (Douglas-Peucker) and turned into Catmull-Rom Béziers. Both neighbouring shapes reuse the
   same curve, so there are no gaps or overlaps. A test checks that the shape areas add up exactly to the canvas.
5. Each number goes at the deepest point of its shape, sized to fit inside it.

## Command line

```bash
cd backend
python -m app.cli sketch photo.jpg -o out.png --preset "Realistic pencil portrait"
python -m app.cli sketch photo.jpg -o out.png --set style=hatch --set levels=5 --set hatch_spacing=10
python -m app.cli pbn photo.jpg -o out.svg --set colors=18 --set min_shape_mm=4 --set print_width_cm=40
python -m app.cli pbn photo.jpg -o out.svg --recipe earlier.recipe.json     # replay a recipe
```

A `.recipe.json` is written next to every output. All parameter names, ranges and defaults are in
`backend/app/engine/schemas.py` (the web app reads them from `GET /api/schema`, so the sliders can't drift
from the engine).

## API

| Endpoint | |
|---|---|
| `GET /api/health`, `/api/schema`, `/api/presets` | status, parameter ranges + defaults, presets |
| `POST /api/process` | multipart: `file`, `mode` (`sketch`/`pbn`), `params` (JSON), `quality` (`preview`/`full`) → JSON with `image` (PNG data URL) or `svg` + `palette`, `stats`, `recipe`, `ms` |
| `POST /api/export` | multipart: `file`, `mode`, `params`, `format` (`png`, `svg_canvas`, `svg_guide`, `svg_painted`, `recipe`) → file download |

Interactive docs at http://localhost:8000/docs.

## Tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest
```

32 tests: determinism for every style, seed behaviour, PBN colour count / numbering / minimum shape size,
exact shape-area closure, SVG validity and layers, API formats and error handling, recipe replay.
Tests use a generated image, so they need no downloads.

## What to know before you rely on it

- **Tuned on two photos** (a portrait and a cat) plus a synthetic image. Run it on real customer photos and
  adjust the presets in `backend/app/presets.py`. Good presets are most of the quality.
- **Faces in paint-by-numbers** need more colours (24–32) and a small minimum shape (3 mm) for a good likeness;
  at low colour counts small features such as eyes can disappear into a neighbouring shape. A future
  improvement is to weight k-means towards the detail box.
- **Pencil realism comes from the photo.** Sharp, well-lit photos give the best drawings; the engine cannot
  invent detail that isn't in the picture. A blur / resolution check on upload would be a good addition.
- Full-resolution PBN takes roughly 5–15 s depending on size and colour count; sketches take under a second.
  The API runs renders in worker threads; for several users at once, run uvicorn with `--workers 2+` or add a job queue.
- No accounts, storage or payments. Uploads are processed in memory and not saved.

## Ideas for the next phase

A/B-tile printing with registration marks, paint-brand colour matching and mix recipes, batch mode for a folder
of photos, background removal toggle, saved per-customer jobs, detail-weighted colour clustering.

Sample photos: NASA astronaut portrait (public domain) and the "chelsea" cat photo (CC0), both from scikit-image's test data.
