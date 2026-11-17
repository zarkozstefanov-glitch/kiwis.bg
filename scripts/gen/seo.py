"""Build crawlable BG/EN documents and reciprocal metadata using only the stdlib."""
import copy
import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit
from xml.etree import ElementTree as ET

HERE = Path(__file__).resolve().parent
BASE = "https://kiwis.bg"
PAGES = json.loads((HERE / "seo_data.json").read_text())
CONTENT = json.loads((HERE / "english_content.json").read_text())
VOID = set("area base br col embed hr img input link meta param source track wbr".split())


class Node:
    def __init__(self, tag="", attrs=(), children=None):
        self.tag, self.attrs, self.children = tag, dict(attrs), children or []

    def walk(self):
        yield self
        for child in self.children:
            if isinstance(child, Node):
                yield from child.walk()

    def find(self, tag=None, cls=None):
        return next(n for n in self.walk() if (tag is None or n.tag == tag) and (cls is None or cls in n.attrs.get("class", "").split()))

    def text(self):
        return html.unescape("".join(c.text() if isinstance(c, Node) else c for c in self.children))

    def render(self):
        body = "".join(c.render() if isinstance(c, Node) else c for c in self.children)
        if not self.tag:
            return body
        attrs = "".join(" " + k + ("" if v is None else '="' + html.escape(v, quote=True) + '"') for k, v in self.attrs.items())
        return "<" + self.tag + attrs + ">" + ("" if self.tag in VOID else body + "</" + self.tag + ">")


class Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.root = Node()
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        n = Node(tag, attrs)
        self.stack[-1].children.append(n)
        if tag not in VOID:
            self.stack.append(n)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                self.stack = self.stack[:i]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)

    def handle_entityref(self, name):
        self.handle_data("&" + name + ";")

    def handle_charref(self, name):
        self.handle_data("&#" + name + ";")

    def handle_decl(self, data):
        self.handle_data("<!" + data + ">")

    def handle_comment(self, data):
        self.handle_data("<!--" + data + "-->")


def parse(text):
    p = Parser()
    p.feed(text)
    return p.root


def plain(s):
    return re.sub(r"\s+", " ", parse(s).text()).strip()


def node(tag, **attrs):
    return Node(tag, attrs.items())


WORDS = {
    "Начало": "Home", "Назад": "Back", "Меню": "Menu", "Статии": "Articles",
    "Източници": "Sources", "Още статии": "More articles", "Гладен ли си?": "Hungry?",
    "Виж менюто": "View the menu", "Поверителност": "Privacy", "Пловдив": "Plovdiv",
    "Страницата не е намерена": "Page not found", "Меню на Kiwi's": "Kiwi’s menu",
    "ул. „Никола Карев“ 14": "14 Nikola Karev St.", "ул. Никола Карев 14": "14 Nikola Karev St.",
    "Протеинова храна с калории и макроси на всяко ястие — ул. „Никола Карев“ 14, Пловдив.": "Protein food with calories and macros for every dish — 14 Nikola Karev St., Plovdiv.",
    "Как пазим името и имейла ти, когато се запишеш за новини от Kiwi's.": "How we protect your name and email address when you subscribe to Kiwi’s news.",
    "Здравословна храна": "Healthy food", "Протеинова храна": "High-protein food",
    "Сандвичи": "Sandwiches", "Салати": "Salads", "Десерти": "Desserts", "Кафе": "Coffee",
    "Приблизителни хранителни стойности": "Approximate nutrition values",
    "Основна навигация": "Main navigation", "Kiwi's — начало": "Kiwi’s — home",
    "Поръчай с доставка": "Order delivery", "Поръчай в Glovo": "Order on Glovo", "Поръчай в Bolt Food": "Order on Bolt Food",
    "Обади се": "Call us", "Предишно": "Previous", "Следващо": "Next", "Предишна": "Previous", "Следваща": "Next",
    "Виж другата снимка": "View the other photo", "Друга снимка": "Other photo", "Избери": "Choose an item",
    "Надолу": "Scroll down", "Снимки": "Photos", "Затвори": "Close", "Откъси от отзиви": "Review excerpts",
    "Терасата в градината": "The garden terrace", "Барът": "The bar", "Залата": "Inside",
    "Входът": "The entrance", "Кафе на терасата": "Coffee on the terrace", "Порция за из път": "A bowl to go",
    "Протеинов десерт": "Protein dessert", "Бриош сандвич": "Brioche sandwich",
    "Барът на Kiwi's в Пловдив": "The bar at Kiwi’s in Plovdiv",
    "Пилешка порция в Kiwi's пред стената с логото": "A chicken bowl at Kiwi’s in front of the logo wall",
    "Kiwi's на картата — ул. Никола Карев 14, Пловдив": "Kiwi’s on the map — 14 Nikola Karev St., Plovdiv",
    "Храна за вкъщи": "Takeaway", "Тераса в градината": "Garden terrace",
    "България": "Bulgaria", "Български": "Bulgarian", "Статии на Kiwi's": "Kiwi’s articles",
    "Kiwis Пловдив": "Kiwis Plovdiv", "Вегетариански ястия": "Vegetarian options",
    "Пилешка порция": "Chicken bowl",
    "Kiwi's е място за здравословно хранене в Пловдив, ул. „Никола Карев“ 14: протеинови бриош сандвичи, протеинови порции с басмати ориз, салати, протеинови десерти в кен, Cloud Foam напитки, матча и кафе. Калории и макроси на всяко ястие. Зала и тераса в градината. Доставка с Glovo и Bolt Food.": "Kiwi’s serves protein brioche sandwiches, rice bowls, salads, protein desserts, Cloud Foam drinks, matcha and coffee at 14 Nikola Karev St., Plovdiv. Calories and macros are shown for each dish. Indoor seating, a garden terrace and delivery by Glovo and Bolt Food.",
    "/ Статии": "/ Articles", "Статии за здравословно хранене": "Healthy eating articles",
    "Протеин, макроси и как да се храниш добре — кратко, ясно и с източници.": "Protein, macros and eating well — practical articles backed by sources.",
    "Колко протеин на ден е нужен на възрастен, на човек, който тренира, и след 65 години — с препоръките на EFSA и ISSN и примери с реални ястия.": "How much protein adults, active people and people over 65 need each day, with EFSA and ISSN guidance and meal examples.",
    "Какво са макросите, колко калории има в грам протеин, въглехидрати и мазнини, и как да четеш хранителните стойности в менюто.": "What macros are, how many calories protein, carbohydrates and fat provide, and how to read the nutrition values on our menu.",
    "Практични съвети за здравословно хранене в заведение: как да изградиш чинията, какво да внимаваш със сосовете, напитките и солта.": "Practical tips for eating well at a restaurant: build a balanced plate and watch sauces, drinks and salt.",
}
for page in PAGES.values():
    for field in ("title", "description", "heading"):
        if field in page:
            WORDS[page[field]["bg"]] = page[field]["en"]
for cat in json.loads((HERE / "menu_data.json").read_text()):
    WORDS[cat["bg"]] = cat["en"]
    for item in cat.get("items", []):
        WORDS[item["bg"]] = item["en"]
        WORDS[item["dbg"]] = item["den"]
    for en, bg, _ in cat.get("rows", []):
        WORDS[bg] = en


def translated(text, words):
    stripped = text.strip()
    if not stripped:
        return text
    if stripped in words:
        return text.replace(stripped, words[stripped], 1)
    if stripped == "г":
        return text.replace("г", "g")
    if stripped.endswith(" мин четене") and stripped[:-11].isdigit():
        return text.replace(stripped, stripped[:-11] + " min read", 1)
    for bg in sorted(words, key=len, reverse=True):
        if len(bg) > 12 and stripped.startswith(bg):
            text = text.replace(bg, words[bg], 1)
            break
    return re.sub(r"(?<=\d)\s*г\b", " g", text)


def local_url(value, bg_route, english):
    if not value or value.startswith(("#", "data:", "tel:", "mailto:", "javascript:")):
        return value
    u = urlsplit(urljoin(BASE + bg_route, value))
    if u.netloc not in ("kiwis.bg", "www.kiwis.bg"):
        return value
    route = u.path
    if route.endswith("/index.html"):
        route = route[:-10]
    if english and route in PAGES:
        route = PAGES[route]["en"]
    return urlunsplit(("", "", route, u.query, u.fragment))


def schema(value, bg_route, english, words):
    if isinstance(value, list):
        return [schema(v, bg_route, english, words) for v in value]
    if isinstance(value, dict):
        out = {k: schema(v, bg_route, english, words) for k, v in value.items()}
        if english and out.get("inLanguage") == "bg":
            out["inLanguage"] = "en"
        if out.get("@type") == "EntryPoint":
            out["inLanguage"] = "bg" if "glovoapp.com" in out.get("urlTemplate", "") else "en"
        if value.get("@id") == BASE + "/#restaurant":
            out["@id"], out["url"] = BASE + "/#restaurant", BASE + "/"
        if out.get("@type") == "WebSite":
            out["@id"], out["url"], out["inLanguage"] = BASE + "/#website", BASE + "/", ["bg", "en"]
        if out.get("@type") == "Menu":
            out.pop("isPartOf", None)
            out["provider"] = {"@id": BASE + "/#restaurant"}
        return out
    if isinstance(value, str):
        if value.startswith(BASE):
            if value == BASE + "/#restaurant":
                return value
            return BASE + local_url(value, bg_route, english)
        return translated(value, words) if english else value
    return value


def build_document(source, route, cfg, lang):
    doc = parse(source)
    english = lang == "en"
    current = cfg["en"] if english else route
    canonical = BASE + current
    words = dict(WORDS)
    for n in doc.walk():
        if "data-en" in n.attrs:
            words[plain(n.render().split(">", 1)[1].rsplit("</", 1)[0])] = plain(n.attrs["data-en"])
    if english:
        for n in list(doc.walk()):
            if "data-en" in n.attrs:
                n.children = parse(n.attrs["data-en"]).children
        if cfg["kind"] == "article":
            body = doc.find(cls="post-body")
            tail = [n for n in body.children if isinstance(n, Node) and any(c in n.attrs.get("class", "").split() for c in ("sources", "post-cta", "more"))]
            body.children = parse(CONTENT["articles"][route]).children + tail
            doc.find("h1").children = [html.escape(cfg["heading"]["en"])]
        elif cfg["kind"] == "privacy":
            doc.find(cls="post-body").children = parse(CONTENT["privacy"]).children
        for n in doc.walk():
            if n.tag not in ("script", "style"):
                n.children = [html.escape(translated(html.unescape(c), words), quote=False) if isinstance(c, str) and not c.startswith(("<!", "<!--")) else c for c in n.children]
            for attr in ("alt", "title", "aria-label", "placeholder", "content"):
                if attr in n.attrs:
                    n.attrs[attr] = translated(n.attrs[attr], words)
            if "data-en-aria-label" in n.attrs:
                n.attrs["aria-label"] = n.attrs["data-en-aria-label"]
            if "post-meta" in n.attrs.get("class", "").split():
                n.children = [re.sub(r"(\d+) мин четене", r"\1 min read", c) if isinstance(c, str) else c for c in n.children]
    for n in doc.walk():
        for attr in ("href", "src", "data-alt", "data-full"):
            if attr in n.attrs:
                n.attrs[attr] = local_url(n.attrs[attr], route, english)
        for attr in ("srcset", "imagesrcset"):
            if attr in n.attrs:
                n.attrs[attr] = ", ".join(" ".join([local_url(p.split()[0], route, english), *p.split()[1:]]) for p in n.attrs[attr].split(",") if p.strip())
        # Language changes use real links; avoid rewriting hundreds of DOM nodes at load.
        for attr in ("data-en", "data-bg", "data-en-aria-label", "data-bg-aria-label"):
            n.attrs.pop(attr, None)
        if "lang-btn" in n.attrs.get("class", "").split():
            code = n.attrs["data-lang"]
            n.tag = "a"
            n.attrs.update(href=cfg["en"] if code == "en" else route, lang=code, hreflang=code)
            n.attrs["class"] = "lang-btn" + (" is-active" if code == lang else "")
    root = doc.find("html")
    root.attrs.update(lang=lang, **{"data-lang": lang, "data-localized": "true"})
    head = doc.find("head")
    title = doc.find("title")
    title.children = [html.escape(cfg["title"][lang])]
    image = next((n.attrs["content"] for n in head.walk() if n.tag == "meta" and n.attrs.get("property") == "og:image"), BASE + "/images/og-image.jpg")
    if image.startswith("/"):
        image = BASE + image
    metas = {
        "description": cfg["description"][lang], "robots": "noindex, follow" if cfg.get("noindex") else "index, follow, max-image-preview:large",
        "og:type": "article" if cfg["kind"] == "article" else "website", "og:url": canonical,
        "og:title": cfg["title"][lang], "og:description": cfg["description"][lang], "og:site_name": "Kiwi’s",
        "og:locale": "en_GB" if english else "bg_BG", "og:locale:alternate": "bg_BG" if english else "en_GB",
        "og:image": image, "og:image:alt": "Kiwi’s Plovdiv" if english else "Kiwi’s Пловдив",
        "twitter:card": "summary_large_image", "twitter:title": cfg["title"][lang], "twitter:description": cfg["description"][lang],
        "twitter:image": image, "twitter:image:alt": "Kiwi’s Plovdiv" if english else "Kiwi’s Пловдив",
    }
    graph = []
    kept = []
    for n in head.children:
        if isinstance(n, Node):
            if n.tag == "meta" and (n.attrs.get("name") in metas or n.attrs.get("property") in metas):
                continue
            if n.tag == "link" and n.attrs.get("rel") in ("canonical", "alternate"):
                continue
            if n.tag == "script" and n.attrs.get("type") == "application/ld+json":
                data = schema(json.loads(n.text()), route, english, words)
                graph.extend(data.get("@graph", [data]))
                continue
        kept.append(n)
    head.children = kept
    head.children.append(node("link", rel="canonical", href=canonical))
    if not cfg.get("noindex"):
        for code, url in (("bg", route), ("en", cfg["en"]), ("x-default", route)):
            head.children.append(node("link", rel="alternate", hreflang=code, href=BASE + url))
    for key, val in metas.items():
        head.children.append(node("meta", **{"property" if key.startswith("og:") else "name": key, "content": val}))
    if not cfg.get("noindex"):
        if not any(item.get("@type") == "WebSite" for item in graph):
            graph.append({"@type": "WebSite", "@id": BASE + "/#website", "url": BASE + "/", "name": "Kiwi’s", "inLanguage": ["bg", "en"], "publisher": {"@id": BASE + "/#restaurant"}})
        graph.append({"@type": "WebPage", "@id": canonical + "#webpage", "url": canonical, "name": cfg["title"][lang], "description": cfg["description"][lang], "inLanguage": lang, "isPartOf": {"@id": BASE + "/#website"}})
        if cfg["kind"] in ("menu", "blog"):
            graph.append({"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home" if english else "Начало", "item": BASE + ("/en/" if english else "/")},
                {"@type": "ListItem", "position": 2, "name": ("Menu" if cfg["kind"] == "menu" else "Articles") if english else ("Меню" if cfg["kind"] == "menu" else "Статии"), "item": canonical},
            ]})
    if graph:
        head.children.append(Node("script", [("type", "application/ld+json")], [json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2).replace("</", "<\\/")]))
    return doc.render()


def main(out):
    out = Path(out)
    for route, cfg in PAGES.items():
        source = (out / cfg["file"]).read_text()
        for lang in ("bg", "en"):
            url = route if lang == "bg" else cfg["en"]
            file = out / (url.lstrip("/") + ("index.html" if url.endswith("/") else ""))
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(build_document(source, route, cfg, lang))
    ns, xhtml = "http://www.sitemaps.org/schemas/sitemap/0.9", "http://www.w3.org/1999/xhtml"
    ET.register_namespace("", ns)
    ET.register_namespace("xhtml", xhtml)
    sitemap = ET.Element("{" + ns + "}urlset")
    for route, cfg in PAGES.items():
        if cfg.get("noindex"):
            continue
        for current in (route, cfg["en"]):
            entry = ET.SubElement(sitemap, "{" + ns + "}url")
            ET.SubElement(entry, "{" + ns + "}loc").text = BASE + current
            for lang, url in (("bg", route), ("en", cfg["en"]), ("x-default", route)):
                ET.SubElement(entry, "{" + xhtml + "}link", {"rel": "alternate", "hreflang": lang, "href": BASE + url})
    ET.indent(sitemap)
    ET.ElementTree(sitemap).write(out / "sitemap.xml", encoding="utf-8", xml_declaration=True)
    print(f"SEO: {len(PAGES) * 2} localized documents; reciprocal BG/EN metadata and sitemap generated")


if __name__ == "__main__":
    main(sys.argv[1])
