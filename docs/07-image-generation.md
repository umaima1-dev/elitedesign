# 07 · AI image generation — beautiful, not slop

Every photo and 3D render in these designs is AI-generated, then optimized and wired in. This is the workflow that produces *cohesive, on-brand* imagery instead of the random-stock look.

Tools used here: **Magnific** (via its MCP). The same prompts work in **Midjourney, Flux, DALL·E 3, Ideogram, Adobe Firefly**.

## The golden rules
1. **Match the brand, not "AI art."** Prompt the palette and mood explicitly: *"deep oxblood red on near-black, film grain, fine-art editorial."*
2. **Unify a set.** Generate in one consistent style; then grayscale-by-default + color-on-hover, or one duotone grade, so a mixed set reads as one shoot.
3. **Same person = use a reference.** For a personal brand, upload one portrait and generate variations *from it* so every shot is the same face (see below).
4. **Cut out the subject** for hero objects so they sit on your background (remove-background → transparent PNG), then add a CSS glow.
5. **Always optimize** before shipping (resize to display size, ~85% JPEG). A 13 MB hero will tank your page and your deploy.

## Prompt patterns by design

**Dark luxury fashion (Maison Aurél)**
> "Luxury fashion editorial, elegant woman in a flowing champagne silk gown, dark moody background, warm gold rim light, cinematic, subtle film grain, haute couture, photorealistic"

**Dark fine-art editorial (Vessel)**
> "Abstract swirling crimson and black ink in water, dramatic fine-art photography, deep oxblood red on near-black, minimal, elegant"

**Vibrant creative studio (Prisma)**
> "Bold colorful abstract festival poster artwork, vibrant gradients of orange purple green and blue, energetic geometric shapes, modern graphic design"

**Web3 / 3D objects (FabChain)**
> "Single glossy 3D coin with iridescent rainbow reflection, deep navy background, web3, octane render, centered, soft studio reflections"

**Botanical beauty (citrus)**
> "Editorial beauty photo, glowing dewy skin holding a fresh orange slice, vibrant green leaves, bright sunlight, vivid saturated orange and green, clean luxury skincare campaign, photorealistic"

Add to most prompts: `photorealistic` (or `octane render` for 3D), the **exact palette words**, the **mood** (cinematic / moody / bright), and `no text`.

## Same-face consistency (Magnific example)
The trick behind Amara Reed's gallery — one model across five settings:
```
1. Upload a reference portrait → get a creation id
   creations_upload_image({ url: "https://.../portrait.jpg" })   // public URL
2. Generate with that reference + a strong model (Nano Banana Pro / character-consistent):
   images_generate({
     prompt: "the same woman speaking on stage with a microphone, warm spotlight, editorial",
     mode: "imagen-nano-banana-2",
     references: [{ type:"image", identifier:"<creation id>" }],
     aspectRatio: "3:4"
   })
```
Result: the same person, new pose/scene/wardrobe. Repeat for each shot.

## Background removal (hero objects)
```
images_remove_background({ creationIdentifier:"<id>" })   // → transparent PNG creation
```
Download as PNG (preserve alpha), drop a CSS radial-gradient glow behind it. (Don't fake transparency with `mix-blend-mode` on a parent that has a `filter` — it isolates the blend and the black box stays. Cut it out for real.)

## Optimize before shipping
```powershell
# resize to ~1000–1200px wide, 85% JPEG (PNG only if you need alpha)
# (System.Drawing on Windows, ImageMagick, sharp, or squoosh all work)
```
Targets: hero ~1100px, gallery ~800–900px, thumbnails smaller. Aim for <200 KB each.

## Cost & batching
- Generate in **parallel** (fire all prompts, then collect). recraft-v4-1 is fast (~10s) and cheap; Nano Banana Pro is slower/pricier but best for reference consistency and final hero assets.
- Always **look at the result** before wiring it in — regenerate the duds.

## Where to put generated images in code
- **Hover-reveal list:** `data-img="assets/x.jpg"` on each row (recipe #8).
- **Scatter / horizontal gallery / sticky stack:** `<img src="assets/x.jpg">` in the items.
- **Cards / tiles:** `background:url('assets/x.jpg') center/cover` or an `<img>`.
- Unify with a filter: `filter:grayscale(1)` default → `grayscale(0)` on hover, or a duotone `mix-blend` tint in the brand color.
