# 02 · Extracting a real site's design tokens

The fastest way to a beautiful palette and type system is to **lift it from a site you admire** — not by eyeballing screenshots (you'll guess wrong), but by reading its actual CSS. This was the single most important technique in this whole project.

> ⚠️ Extract the *system* (colors, fonts, gradients, scale) to learn and build something new. Don't copy a brand's content, logo, or imagery.

## Why not just screenshot it?
Because your eyes lie. Early on, every design built from a *visual impression* missed — a site described as "premium minimal" turned out to be dark teal + gold, not the light cream that was guessed. **Read the CSS and you stop guessing.**

## The method

### 1. Download the HTML
Browsers/curl sometimes hit TLS issues; PowerShell's `Invoke-WebRequest` with a browser User-Agent is reliable on Windows:

```powershell
$ua = @{ "User-Agent" = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124 Safari/537.36" }
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 -bor [Net.SecurityProtocolType]::Tls13
(Invoke-WebRequest "https://example.com/" -UseBasicParsing -Headers $ua).Content | Out-File site.html -Encoding utf8
```

### 2. Find the stylesheet & font links
```bash
grep -oiE 'href="[^"]+\.css[^"]*"' site.html | sort -u
grep -oiE 'font-family:[^;"}<]+' site.html | sort -u
```
Modern sites (Next.js/Framer) keep CSS in linked chunks — download those too and grep them.

### 3. Pull the colors, ranked by usage
```bash
grep -oiE '#[0-9a-f]{6}' site.css | tr 'A-F' 'a-f' | sort | uniq -c | sort -rn | head -20
grep -oiE 'rgba?\([0-9., ]+\)'   site.css | sort | uniq -c | sort -rn | head -15
```
The **most frequent** hexes are almost always the background + primary text + accent. That's your core palette.

### 4. Pull the gradients (the signature)
```bash
grep -oiE 'linear-gradient\([^)]{0,120}\)' site.css | sort -u | head
```
A site's signature is often one gradient. ApeChain's was `linear-gradient(45deg,#a281ff,#eb8280,#ebbf9a,#89d0ff)` — extracting it exactly is what made the FabChain rebuild feel right.

### 5. Pull the fonts & the type scale
```bash
grep -oiE 'font-family:[^;{}]+'  site.css | sort | uniq -c | sort -rn
grep -oiE '\--fs-[a-z0-9]+:[^;]+' site.css | sort -u    # framer/design-token scales
```
You'll often find paid display fonts (Manuka, PP Eiko, PP Otherside). Substitute the closest free Google Font (see [`03-typography.md`](03-typography.md)).

### 6. Pull CSS custom properties (design tokens)
```bash
grep -oiE '\--[a-z0-9-]+:[^;{}]+' site.css | sort -u | head -60
```
Framer/Tailwind sites expose full token scales (`--color-green-500: 155 85% 29%` etc.) — pure gold for rebuilding faithfully.

## What you walk away with
A short token block you can paste straight into `:root`:

```css
:root{
  --bg:#020315;            /* most-frequent dark hex */
  --ink:#eaf1ff;
  --accent:#0086ff;        /* the bright one */
  --rainbow:linear-gradient(45deg,#a281ff,#eb8280,#ebbf9a,#89d0ff);
  /* fonts: Anton (sub for Manuka) + DM Sans + DM Mono */
}
```

Now you're building in the reference's real language — and free to make something entirely your own with it.

## Cleanup
Delete the downloaded `site.html` / `site.css` scratch files when done.
