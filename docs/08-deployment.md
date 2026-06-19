# 08 · Deployment

These are static files — they deploy anywhere. The whole gallery in this repo was shipped to Netlify.

## Option A — Netlify Drop (no account-CLI, 60 seconds)
1. Sign in at [netlify.com](https://netlify.com) (free).
2. Go to **[app.netlify.com/drop](https://app.netlify.com/drop)**.
3. Drag the `examples/` folder (or a zip of it) onto the page.
4. You get a live URL instantly; rename it in **Site settings → Change site name**.

`index.html` must be at the root of what you drop, so it loads as the homepage.

## Option B — Netlify via connector / CLI (re-deployable)
If you've connected Netlify (MCP) or installed the CLI, deploy the publish folder:
```bash
# CLI
netlify deploy --prod --dir examples
```
With a `netlify.toml` you can set the publish dir:
```toml
[build]
  publish = "."     # if you run it from inside the folder
  command = ""
```

## Option C — GitHub Pages (free, from the repo)
1. Push this repo to GitHub.
2. Repo **Settings → Pages → Deploy from branch** → `main` / root (or `/examples`).
3. Live at `https://<user>.github.io/<repo>/examples/`.

## Option D — Vercel
Import the GitHub repo at [vercel.com/new](https://vercel.com/new); set the output/root to `examples`. Auto-deploys on every push.

## Gotchas learned shipping this
- **Optimize images first** (see [`07`](07-image-generation.md)) — a multi-MB hero bloats the deploy and slows first paint.
- **Relative paths only** (`assets/x.jpg`, not `/Users/...`). Everything resolves from the page's folder.
- **Removing a page from the gallery ≠ removing the file.** Some deploy methods are additive and keep old files. To truly retire a page, delete the file *and* add a forced redirect:
  ```
  # _redirects  (Netlify)
  /old-page.html   /   301!
  ```
  The `!` forces the redirect even if the old file still exists in the deploy.
- **Hard-refresh** (Ctrl/Cmd+Shift+R) after redeploys; CDNs cache.
