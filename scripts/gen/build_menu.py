import json, sys, re
sys.path.insert(0, sys.argv[1])
from pv_lib import viewer, e, GLOVO, nav, footer, sticky_order, price_bg, price_en
S, OUT = sys.argv[1], sys.argv[2]
cats = json.load(open(f"{S}/menu_data.json"))
BASE = "https://kiwis.bg/"
VEG = {"Вегетариански Бриош", "Вегетарианска порция", "Вегетарианска салата"}

BACK = '<a class="back-link back-link--dark" href="index.html" data-back aria-label="Назад"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg></a>'
NOUN = {"cloud": ("напитки", "drinks"), "sandwich": ("сандвича", "sandwiches"), "portion": ("порции", "bowls"),
        "salad": ("салати", "salads"), "dessert": ("десерта", "desserts")}
SUBS = {
    "cloud": ("Пяна от мляко върху студено кафе, матча или плодово пюре.", "Milk foam over iced coffee, matcha or fruit purée."),
    "sandwich": ("Протеинов бриош, изпечен при нас, с прясна плънка.", "Protein brioche baked in-house, freshly filled."),
    "portion": ("Месо или риба, басмати ориз и много зеленчуци.", "Meat or fish, basmati rice and plenty of vegetables."),
    "salad": ("Големи салати с протеинов дресинг.", "Big salads with a protein dressing."),
    "dessert": ("Протеинови десерти в кен, 250 г.", "Protein desserts in a can, 250 g."),
}

sections_html = ""
ld_sections = []
num = 0
for c in cats:
    cid = c["id"]
    if c.get("items"):
        for it in c["items"]:
            it["cat"] = cid
        prices = sorted(float(i["price"]) for i in c["items"])
        lo, hi = prices[0], prices[-1]
        rng = price_bg(lo) if lo == hi else f'{price_bg(lo)[:-2]} – {price_bg(hi)}'
        rng_en = price_en(lo) if lo == hi else f'{price_en(lo)} – {price_en(hi)}'
        nb, ne = NOUN[cid]
        sub_bg, sub_en = SUBS.get(cid, ("", ""))
        num += 1
        WORD = {"cloud": "Foam", "sandwich": "Brioche", "portion": "Bowls", "salad": "Fresh", "dessert": "Sweet"}.get(cid, "")
        sections_html += f'''
    <section class="cat cat--green" id="{cid}" data-category="{cid}" aria-labelledby="h-{cid}">
      <span class="cat-word" aria-hidden="true">{WORD}</span>
      <div class="container">
        <div class="cat-head" data-reveal="left">
          <div><span class="cat-top">{BACK if num == 1 else ""}<span class="cat-num">{num:02d}</span></span><h2 id="h-{cid}" data-en="{e(c["en"])}">{e(c["bg"])}</h2></div>
          <span class="cat-meta" data-en="{len(c["items"])} {ne} · {rng_en}">{len(c["items"])} {nb} · {rng}</span>
        </div>
        {viewer("pv-" + cid, c["items"], loop=True, bare=True)}
      </div>
    </section>
'''
        items_ld = []
        for it in c["items"]:
            d = {"@type": "MenuItem", "name": it["bg"], "description": it["dbg"] + (f" ({it['w']})" if it["w"] else ""),
                 "offers": {"@type": "Offer", "price": f'{float(it["price"]):.2f}', "priceCurrency": "EUR", "availability": "https://schema.org/InStock"},
                 "nutrition": {"@type": "NutritionInformation", "calories": f'{it["k"]} kcal', "proteinContent": f'{it["p"]} g',
                               "carbohydrateContent": f'{it["c"]} g', "fatContent": f'{it["f"]} g'}}
            if it["w"]:
                d["nutrition"]["servingSize"] = it["w"].replace(" г", " g")
            if it.get("img") and it["img"] not in ("cloud-matcha", "cloud-blueberry"):
                d["image"] = f'{BASE}images/cut/{it["img"]}-1-900.webp'
            if it["bg"] in VEG:
                d["suitableForDiet"] = "https://schema.org/VegetarianDiet"
            items_ld.append(d)
        ld_sections.append({"@type": "MenuSection", "name": c["bg"], "url": f"{BASE}menu.html#{cid}", "hasMenuItem": items_ld})
    else:
        rows = "".join(f'<li><span data-en="{e(en)}">{e(bg)}</span><b data-en="{price_en(pr)}">{price_bg(pr)}</b></li>' for en, bg, pr in c["rows"])
        sections_html += f'''
    <section class="cat cat--drinks" id="{cid}" data-category="{cid}" aria-labelledby="h-{cid}">
      <div class="container">
        <div class="cat-head"><div><span class="cat-top"><span class="cat-num">{num + 1:02d}</span></span><h2 id="h-{cid}" data-en="{e(c["en"])}">{e(c["bg"])}</h2></div><span class="cat-meta" data-en="{len(c["rows"])} drinks · from {price_en(min(float(r[2]) for r in c["rows"]))}">{len(c["rows"])} напитки · от {price_bg(min(float(r[2]) for r in c["rows"]))}</span></div>
        <ul class="drinks">{rows}</ul>
      </div>
    </section>
'''
        ld_sections.append({"@type": "MenuSection", "name": c["bg"], "url": f"{BASE}menu.html#{cid}", "hasMenuItem": [
            {"@type": "MenuItem", "name": bg, "offers": {"@type": "Offer", "price": f"{float(pr):.2f}", "priceCurrency": "EUR"}} for en, bg, pr in c["rows"]]})

ld = {"@context": "https://schema.org", "@type": "Menu", "@id": f"{BASE}menu.html#menu", "name": "Меню на Kiwi's", "url": f"{BASE}menu.html",
      "inLanguage": "bg", "isPartOf": {"@type": "Restaurant", "@id": f"{BASE}#restaurant", "name": "Kiwi's"}, "hasMenuSection": ld_sections}

old = open(OUT, encoding="utf-8").read()
head = old[:old.index('<script type="application/ld+json">')]
VT = '<style>@view-transition{navigation:auto}</style>'   # must be inline: Chrome ignores the opt-in from an external sheet here
if VT not in head:
    head = head.replace('<meta charset="UTF-8">', '<meta charset="UTF-8">\n  ' + VT, 1)
head = head.replace('<link rel="stylesheet" href="css/menu.css">', '<link rel="stylesheet" href="css/pv.css">\n  <link rel="stylesheet" href="css/menu.css">') if 'css/pv.css' not in head else head
BIKE = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 17h-2v-6l2-5h9l4 5h1a2 2 0 012 2v4h-2"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/><path d="M9 17h6"/></svg>'
CALL = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.86 19.86 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.86 19.86 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72c.12.96.36 1.9.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.91.34 1.85.58 2.81.7A2 2 0 0122 16.92z"/></svg>'
body = f'''  <script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
  </script>
</head>
<body class="page-menu">
{nav("menu")}
  <main class="menu" id="main">
    <h1 class="sr-only" data-en="Kiwi's menu">Меню на Kiwi's</h1>
{sections_html}
    <p class="menu-foot" data-en="Allergens and ingredients — ask our team or call +359 892 632 470.">Алергени и съставки — попитайте на място или на +359 892 632 470.</p>
  </main>
{footer("menu")}
{sticky_order()}

  <script src="js/pv.js"></script>
  <script src="js/main.js"></script>
</body>
</html>
'''
open(OUT, "w", encoding="utf-8").write(head + body)
print("menu ok", len(ld_sections))
