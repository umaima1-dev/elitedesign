#!/usr/bin/env python3
"""Fetch a website and summarise what a brand profile needs. Standard library only.

Usage:  site_snapshot.py https://example.com [--out business-brain/site-snapshot.md] [--max-pages 6]
        site_snapshot.py --html saved-page.html      (offline, for testing or blocked sites)

Writes a markdown snapshot: title, descriptions, headings, calls to action, copy
excerpts, colours, fonts, social links. It reports facts found on the page. The
setup skill turns them into brand files and asks the user to confirm each one.
Exit 2 if the site cannot be fetched (the skill then asks the user to paste text).
"""
import argparse, collections, re, sys
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

UA = "Mozilla/5.0 (compatible; ContentOS-SiteSnapshot/1.0)"
KEY = re.compile(r"about|pricing|price|service|work-with|offer|program|course|coach|consult|shop|product|testimonial|results|case|faq|story", re.I)
SOCIAL = ("instagram.com", "linkedin.com", "tiktok.com", "youtube.com", "twitter.com", "x.com", "facebook.com", "threads.net", "substack.com")

class P(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""; self.meta = {}; self.h = []; self.p = []; self.links = []
        self.ctas = []; self.styles = []; self.css_links = []; self.fonts = []
        self._tag = None; self._buf = []; self._skip = 0; self._href = None; self._in_style = False
    def handle_starttag(self, tag, a):
        a = dict(a)
        if tag in ("script", "noscript", "svg"): self._skip += 1
        if tag == "style": self._in_style = True; self._buf = []
        if tag == "meta":
            k = a.get("name") or a.get("property")
            if k and a.get("content"): self.meta[k.lower()] = a["content"]
        if tag == "link" and a.get("href"):
            if "stylesheet" in (a.get("rel") or ""):
                if "fonts.googleapis.com" in a["href"]: self.fonts.append(a["href"])
                else: self.css_links.append(a["href"])
        if tag == "a":
            self._href = a.get("href"); 
            if self._href: self.links.append(self._href)
        if "style" in a and a["style"]: self.styles.append(a["style"])
        if tag in ("title", "h1", "h2", "h3", "p", "li", "button", "a"):
            self._tag = tag; self._buf = []
    def handle_endtag(self, tag):
        if tag in ("script", "noscript", "svg") and self._skip: self._skip -= 1
        if tag == "style":
            self.styles.append("".join(self._buf)); self._in_style = False; self._buf = []
            return
        if tag == self._tag:
            t = " ".join("".join(self._buf).split())
            if t:
                if tag == "title": self.title = t
                elif tag in ("h1", "h2", "h3"): self.h.append((tag, t))
                elif tag in ("p", "li") and len(t) > 40: self.p.append(t)
                elif tag in ("button", "a") and 2 <= len(t) <= 40: self.ctas.append(t)
            self._tag = None; self._buf = []
    def handle_data(self, d):
        if self._in_style or (self._tag and not self._skip): self._buf.append(d)

def fetch(url, limit=1_500_000):
    if urlparse(url).scheme not in ("http", "https"):
        raise ValueError("only http(s) URLs")
    with urlopen(Request(url, headers={"User-Agent": UA}), timeout=20) as r:
        return r.read(limit).decode(r.headers.get_content_charset() or "utf-8", "replace")

def parse(html):
    p = P(); p.feed(html); return p

def colours(css_texts):
    c = collections.Counter()
    for css in css_texts:
        for h in re.findall(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b", css):
            h = h.lower()
            if len(h) == 3: h = "".join(x * 2 for x in h)
            c["#" + h] += 1
    return c.most_common(10)

def fonts(css_texts, links):
    c = collections.Counter()
    for css in css_texts:
        for m in re.findall(r"font-family\s*:\s*([^;}{]+)", css):
            first = m.split(",")[0].strip().strip("'\"")
            if first and not first.startswith("var(") and first.lower() not in ("inherit", "initial"):
                c[first] += 1
    for l in links:
        for fam in re.findall(r"family=([^&:]+)", l):
            c[fam.replace("+", " ")] += 3
    return c.most_common(6)

def snapshot(url=None, html=None, max_pages=6):
    pages = []; css_texts = []; font_links = []; socials = set(); errors = []
    if html is not None:
        pages.append((url or "local file", parse(html)))
    else:
        home = fetch(url); hp = parse(home); pages.append((url, hp))
        base = urlparse(url)
        seen = {url.rstrip("/")}
        for href in hp.links:
            u = urljoin(url, href.split("#")[0])
            pu = urlparse(u)
            if pu.netloc == base.netloc and KEY.search(pu.path) and u.rstrip("/") not in seen and len(pages) < max_pages:
                seen.add(u.rstrip("/"))
                try: pages.append((u, parse(fetch(u))))
                except Exception as e: errors.append(f"{u}: {e}")
        for l in hp.css_links[:3]:
            try: css_texts.append(fetch(urljoin(url, l), 400_000))
            except Exception as e: errors.append(f"{l}: {e}")
    for _, pg in pages:
        css_texts += pg.styles; font_links += pg.fonts
        for l in pg.links:
            if any(s in l for s in SOCIAL): socials.add(l.split("?")[0])
    out = [f"# Site snapshot\n\nSource: {url or 'local file'}\n\nFacts read from the page. Not yet confirmed by the owner.\n"]
    h = pages[0][1]
    out.append(f"## Home\n- Title: {h.title}\n- Description: {h.meta.get('description') or h.meta.get('og:description', '')}\n- Social image / og:title: {h.meta.get('og:title', '')}\n")
    for u, pg in pages:
        out.append(f"## Page: {u}")
        hs = [f"{t.upper()}: {x}" for t, x in pg.h[:12]]
        if hs: out.append("Headings:\n" + "\n".join("- " + x for x in hs))
        if pg.p: out.append("Copy excerpts:\n" + "\n".join("- " + x[:300] for x in pg.p[:6]))
        ct = list(dict.fromkeys(pg.ctas))[:12]
        if ct: out.append("Buttons and links (possible CTAs): " + "; ".join(ct))
        out.append("")
    cl = colours(css_texts)
    out.append("## Colours (by frequency in CSS)\n" + ("\n".join(f"- {c} ({n})" for c, n in cl) if cl else "- none found (site may use JS-injected styles)"))
    fl = fonts(css_texts, font_links)
    out.append("\n## Fonts\n" + ("\n".join(f"- {f} ({n})" for f, n in fl) if fl else "- none found"))
    out.append("\n## Social links\n" + ("\n".join("- " + s for s in sorted(socials)) if socials else "- none found"))
    if errors: out.append("\n## Fetch problems\n" + "\n".join("- " + e for e in errors))
    return "\n".join(out) + "\n"

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("url", nargs="?")
    ap.add_argument("--html")
    ap.add_argument("--out", default="business-brain/site-snapshot.md")
    ap.add_argument("--max-pages", type=int, default=6)
    a = ap.parse_args(argv)
    if not a.url and not a.html: ap.error("give a URL or --html")
    try:
        md = snapshot(a.url, open(a.html, encoding="utf-8", errors="replace").read() if a.html else None, a.max_pages)
    except Exception as e:
        print(f"Could not fetch site: {e}", file=sys.stderr); return 2
    open(a.out, "w", encoding="utf-8").write(md)
    print(f"wrote {a.out}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
