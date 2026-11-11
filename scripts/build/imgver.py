"""Cache-busting for images: every images/... URL in the built HTML gets ?v=<content hash>.
Images are cached for 30 days, so a changed photo must get a new URL to reach visitors."""
import hashlib, re, sys
from pathlib import Path

out = Path(sys.argv[1])
cache = {}


def ver(path):
    if path not in cache:
        f = out / path
        cache[path] = hashlib.md5(f.read_bytes()).hexdigest()[:8] if f.is_file() else None
    return cache[path]


pat = re.compile(r'(?P<pre>/?)(?P<path>images/[A-Za-z0-9_./-]+\.(?:webp|jpg|jpeg|png|avif|svg))(?![?\w])')
for page in list(out.glob("*.html")) + list(out.glob("blog/*.html")):
    s = page.read_text(encoding="utf-8")
    s = pat.sub(lambda m: m.group(0) + (f"?v={ver(m.group('path'))}" if ver(m.group("path")) else ""), s)
    page.write_text(s, encoding="utf-8")
print("image versions:", sum(1 for v in cache.values() if v))
