"""Optional helper. Fills the {{file}} tokens in every snippet with your GHL media URLs.
Usage:  python3 fill_urls.py     (reads media-urls.txt, writes the ready files to ./ready/)"""
import glob, os, re
urls = {}
for line in open('media-urls.txt'):
    if '=' in line and not line.startswith('#'):
        k, v = line.strip().split('=', 1)
        if v.strip(): urls[k.strip()] = v.strip()
os.makedirs('ready', exist_ok=True)
for f in sorted(glob.glob('[0-9]*.html')):
    t = open(f).read()
    t = re.sub(r'\{\{([^}]+)\}\}', lambda m: urls.get(m.group(1), m.group(0)), t)
    open('ready/' + f, 'w').write(t)
    left = sorted(set(re.findall(r'\{\{([^}]+)\}\}', t)))
    print(f, 'OK' if not left else 'still missing: ' + ', '.join(left))
