# 01 · Design principles — how to not "scream AI"

The difference between a generated-looking page and a studio-grade one is rarely the layout. It's taste applied through restraint. These are the rules this playbook lives by.

## 1. Restraint reads as expensive
- **One accent colour.** Maison Aurél is black + *one* gold. Vessel is black + *one* oxblood red. The moment you have three bright competing colours, it looks like a demo.
- **Generous whitespace.** Luxury = space. Section padding of `120–220px` is normal here, not excessive.
- **Limited type.** One display face + one workhorse sans. Never more than two families (a mono for labels is the only exception).

## 2. Slow, confident motion
- Luxury/editorial easing is **slow and heavy**: `expo.out`, `power3/4.out`, durations `1.1–1.8s`. Snappy 0.3s eases feel cheap for premium brands.
- Playful brands (Prisma, FabChain) *can* be faster and bouncier — match motion to personality.
- Smooth scroll (Lenis) under everything. It's the single biggest perceived-quality upgrade.

## 3. Steal the system, not the pixels
Don't copy a site. **Extract its tokens** (exact colors, fonts, gradients) and build something new in that language. See [`02-extracting-real-sites.md`](02-extracting-real-sites.md). This is how all 5 designs were made — each is a faithful *interpretation*, not a clone.

## 4. Real imagery, unified — or none
Random stock photos are the #1 tell of a thrown-together page. Lessons learned the hard way:
- **Picsum/random photos clash** with any theme. They wrecked an early steampunk build.
- **Generate cohesive imagery** matched to the brand (see [`07-image-generation.md`](07-image-generation.md)).
- **Unify a mixed set**: default everything to grayscale and reveal colour on hover, or apply a single duotone/grade. This makes disparate images read as one art-directed set.
- **For a person/brand, keep the same face** — generate from a reference image so every shot is the same model.

## 5. Type is 70% of the look
Big, confident display type with tight negative letter-spacing (`-0.02 to -0.04em`) on headings does more than any effect. Pair a characterful display face with a neutral body. See [`03-typography.md`](03-typography.md).

## 6. Texture and depth, quietly
- A **film-grain overlay** at 4–6% opacity (`mix-blend: overlay`) instantly adds analog richness.
- Soft **vignettes** and **radial glows** create depth on dark themes.
- **Layered backgrounds**: e.g. animated gradient blobs *behind* the content, never competing with text (keep text on its own z-layer and legible).

## 7. Native vs custom cursor — choose deliberately
Custom cursors (a dot + trailing ring) feel "designed" but can confuse and annoy on content/commerce pages. Rules we settled on:
- **Editorial/portfolio/luxury showcase** → a custom cursor can elevate.
- **Commerce, SaaS, anything functional** → keep the **native cursor**. Don't make people hunt for their pointer.
- If you remove a custom cursor, also remove `cursor:none` from `body` and delete the cursor elements/JS.

## 8. Make text bulletproof against animation
When images or icons animate near text:
- Keep text on a **higher z-index** so it's never obscured.
- Place decorative elements in the **margins/gaps**, not behind headlines.
- Verify there are **zero overlaps** with the actual glyph boxes, not just the element box.
- Hide busy decoration on small screens where space is tight.

## 9. Ship it
A design isn't finished until it's on a URL. See [`08-deployment.md`](08-deployment.md).

## 10. Verify, don't assume
Open the page. Check the console for errors. Confirm images actually load and animations actually fire (read live values, not just "it should work"). Most "it's broken" moments are a tiny detail — a stacking context, a load-timing race, a wrong path.
