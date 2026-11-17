"""Check the built pages' language, canonical URLs and crawlable links."""
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gen"))
from seo import BASE, PAGES, parse  # noqa: E402


def check(out):
    errors = []
    indexable = set()
    for bg, cfg in PAGES.items():
        for lang, route in (("bg", bg), ("en", cfg["en"])):
            file = out / (route.lstrip("/") + ("index.html" if route.endswith("/") else ""))
            if not file.exists():
                errors.append(f"Missing page: {route}")
                continue
            doc = parse(file.read_text())
            root, head = doc.find("html"), doc.find("head")
            canonical = BASE + route
            if root.attrs.get("lang") != lang or root.attrs.get("data-localized") != "true":
                errors.append(f"Wrong document language: {route}")
            if doc.find("title").text() != cfg["title"][lang]:
                errors.append(f"Wrong title: {route}")
            metas = [n for n in head.walk() if n.tag == "meta"]
            links = [n for n in head.walk() if n.tag == "link"]
            matching = lambda key, val: [n for n in metas if n.attrs.get(key) == val]
            if [n.attrs.get("href") for n in links if n.attrs.get("rel") == "canonical"] != [canonical]:
                errors.append(f"Wrong canonical: {route}")
            if len(matching("name", "description")) != 1 or matching("name", "description")[0].attrs.get("content") != cfg["description"][lang]:
                errors.append(f"Wrong description: {route}")
            if len(matching("property", "og:url")) != 1 or matching("property", "og:url")[0].attrs.get("content") != canonical:
                errors.append(f"Wrong Open Graph URL: {route}")
            alternates = {n.attrs.get("hreflang"): n.attrs.get("href") for n in links if n.attrs.get("rel") == "alternate"}
            expected = {"bg": BASE + bg, "en": BASE + cfg["en"], "x-default": BASE + bg}
            if not cfg.get("noindex"):
                indexable.add(canonical)
                if alternates != expected:
                    errors.append(f"Wrong language alternates: {route}")
            elif alternates or not any("noindex" in n.attrs.get("content", "") for n in matching("name", "robots")):
                errors.append(f"Wrong noindex state: {route}")
            buttons = {n.attrs.get("data-lang"): n.attrs.get("href") for n in doc.walk() if "lang-btn" in n.attrs.get("class", "").split()}
            if cfg["kind"] != "error" and buttons != {"bg": bg, "en": cfg["en"]}:
                errors.append(f"Wrong language buttons: {route}")
            if any("data-en" in n.attrs or "data-bg" in n.attrs for n in doc.walk()):
                errors.append(f"Runtime translation attributes left: {route}")
            schema_nodes = []
            for n in doc.walk():
                if n.tag == "script" and n.attrs.get("type") == "application/ld+json":
                    try:
                        value = json.loads(n.text())
                        schema_nodes.extend(value.get("@graph", [value]))
                    except ValueError:
                        errors.append(f"Invalid JSON-LD: {route}")
                for key in ("href", "src", "data-alt", "data-full"):
                    value = n.attrs.get(key, "")
                    parsed = urlsplit(value)
                    if parsed.netloc in ("kiwis.bg", "www.kiwis.bg") or value.startswith("/"):
                        path = parsed.path
                        if not path or path == "/":
                            continue
                        target = out / (path.lstrip("/") + ("index.html" if path.endswith("/") else ""))
                        if not target.is_file():
                            errors.append(f"Broken local {key} in {route}: {value}")
            ids = [n["@id"] for n in schema_nodes if isinstance(n, dict) and "@id" in n]
            if len(ids) != len(set(ids)):
                errors.append(f"Duplicate JSON-LD IDs: {route}")
            if not cfg.get("noindex") and sum(n.get("@type") == "WebSite" for n in schema_nodes if isinstance(n, dict)) != 1:
                errors.append(f"Missing or duplicate WebSite entity: {route}")
    sitemap = ET.parse(out / "sitemap.xml")
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9", "x": "http://www.w3.org/1999/xhtml"}
    entries = sitemap.findall("s:url", ns)
    actual = {entry.find("s:loc", ns).text for entry in entries}
    if actual != indexable or len(entries) != len(indexable):
        errors.append("Sitemap and indexable canonical URLs differ")
    for entry in entries:
        alternate = {n.attrib["hreflang"]: n.attrib["href"] for n in entry.findall("x:link", ns)}
        if set(alternate) != {"bg", "en", "x-default"}:
            errors.append(f"Missing sitemap alternates: {entry.find('s:loc', ns).text}")
    if errors:
        raise SystemExit("SEO check failed:\n" + "\n".join(sorted(set(errors))))
    print(f"SEO check OK: {len(PAGES) * 2} pages, {len(indexable)} sitemap URLs, valid internal links and JSON-LD")


if __name__ == "__main__":
    check(Path(sys.argv[1]))
