import sys, json
S, OUT = sys.argv[1], sys.argv[2]
sys.path.insert(0, S)
from pv_lib import viewer, e, GLOVO, nav, footer, sticky_order, price_bg, price_en, IG, IG_ICON

head = open(f"{S}/head.html", encoding="utf-8").read()
reviews = open(f"{S}/reviews_snippet.html", encoding="utf-8").read()
revs = json.load(open(f"{S}/rv/all.json"))
cats = json.load(open(f"{S}/menu_data.json"))
ITEMS = {it["bg"]: dict(it, cat=c["id"]) for c in cats for it in c.get("items", [])}

GMAP = "https://www.google.com/maps?cid=1892105797985093642"
DIR = "https://www.google.com/maps/dir/?api=1&amp;destination=Kiwi%27s%2C%20%D1%83%D0%BB.%20%D0%9D%D0%B8%D0%BA%D0%BE%D0%BB%D0%B0%20%D0%9A%D0%B0%D1%80%D0%B5%D0%B2%2014%2C%20%D0%9F%D0%BB%D0%BE%D0%B2%D0%B4%D0%B8%D0%B2"
CALL = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.86 19.86 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.86 19.86 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72c.12.96.36 1.9.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.91.34 1.85.58 2.81.7A2 2 0 0122 16.92z"/></svg>'
BIKE = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 17h-2v-6l2-5h9l4 5h1a2 2 0 012 2v4h-2"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/><path d="M9 17h6"/></svg>'
STAR = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01z"/></svg>'


def photo(name, sizes, alt, w=1000, h=1333):
    if name == "hero":
        srcset, w, h = "images/hero-800.webp 800w, images/hero-1400.webp 1400w, images/hero-2000.webp 2000w", 1600, 1200
    else:
        srcset = f"images/{name}-600.webp 600w, images/{name}-1000.webp 1000w, images/{name}-1600.webp 1600w"
    return (f'<picture><source type="image/webp" srcset="{srcset}" sizes="{sizes}">'
            f'<img src="images/{name}.jpg" width="{w}" height="{h}" alt="{alt}" loading="lazy" decoding="async"></picture>')


# --- dishes our guests name in their Google reviews (quotes are verbatim) ---
PRAISED = [
    ("Манго и кокос протеинов чийзкейк", "Десертите с манго и тирамису бяха чудесен завършек на преживяването!", "Dimitar D."),
    ("Телешки Бриош", "Бриошът е абсолютен ТОР! Невероятно пухкав, ухаещ на масло и доведен до съвършенство", "Videlina S."),
    ("Телешка порция", "Телешкото е невероятно вкусно, порциите са перфектни, а цените – повече от разумни за качеството.", "miroslava t."),
    ("Свински Бриош", "Най-добрият сандвич с дърпано свинско месо", "Goran C."),
    ("Тирамису Cloud Foam", "Храната е отлична, а ice latte tiramisu беше звездата.", "Nicole G."),
]
praised = []
for name, q, by in PRAISED:
    it = dict(ITEMS[name]); it["quote"], it["quote_by"] = q, by
    praised.append(it)

# --- menu categories ---
# names, counts and prices come from the menu itself, so the cards always match menu.html
CARD_IMG = {"cloud": "cloud-caramel-2", "sandwich": "pork-brioche-2", "portion": "chicken-portion-1",
            "salad": "caesar-salad-1", "dessert": "dessert-oreo-1", "coffee": "coffee-frappe-1"}
NOUN = {"cloud": ("напитки", "drinks"), "sandwich": ("сандвича", "sandwiches"), "portion": ("порции", "bowls"),
        "salad": ("салати", "salads"), "dessert": ("десерта", "desserts"), "coffee": ("напитки", "drinks")}
CATS = []
for c in cats:
    ps = sorted(float(i["price"]) for i in c["items"]) if c.get("items") else sorted(float(r[2]) for r in c["rows"])
    cnt = len(c.get("items") or c["rows"])
    nb, ne = NOUN[c["id"]]
    if ps[0] == ps[-1]:
        sub, sen = f"{cnt} {nb} · {price_bg(ps[0])}", f"{cnt} {ne} · {price_en(ps[0])}"
    else:
        sub, sen = f"{cnt} {nb} · от {price_bg(ps[0])}", f"{cnt} {ne} · from {price_en(ps[0])}"
    CATS.append((c["id"], CARD_IMG[c["id"]], e(c["bg"]), e(c["en"]), sub, sen))
cat_html = ""
for i, (cid, img, bg, en, sub, sen) in enumerate(CATS):
    pic = (f'<img src="images/cut/{img}-500.webp" srcset="images/cut/{img}-500.webp 500w, images/cut/{img}-900.webp 900w" sizes="(min-width: 960px) 260px, 44vw" width="900" height="900" alt="" loading="lazy" decoding="async">'
           if img else '<img class="ct-photo" src="images/nest-frappe-600.webp" width="600" height="800" alt="" loading="lazy" decoding="async">')
    cat_html += f'''        <a class="ct ct--{cid}" href="menu.html#{cid}" data-reveal="{"left" if i % 2 == 0 else "right"}">
          <span class="ct-glow" aria-hidden="true"></span>{pic}
          <span class="ct-txt"><b data-en="{en}">{bg}</b><small data-en="{sen}">{sub}</small></span>
          <span class="ct-go" aria-hidden="true">&rarr;</span>
        </a>
'''

# --- review marquee (text reviews only, two rows) ---
COLORS = ["#2E4A32", "#7FAF3A", "#C98A1B", "#3D6344", "#B5654A", "#5A7D8C"]
skip = {"Александър Трайков", "Anna Gateva"}
txt = [r for r in revs if r[5].strip() and r[0] not in skip and len(r[5]) < 330]


def short(n):
    p = n.split()
    return p[0] if len(p) == 1 else f"{p[0]} {p[1][0]}."


def mcard(r, k):
    t = e(r[5].strip().replace("​", "").replace("\n", " "))
    return (f'<figure class="mq-card"><div class="mq-stars">{STAR * 5}</div><blockquote>„{t}“</blockquote>'
            f'<figcaption><span class="mq-av" style="background:{COLORS[k % 6]}">{e(short(r[0])[0].upper())}</span>{e(short(r[0]))}</figcaption></figure>')


ROWS = ["".join(mcard(r, k + j) for k, r in enumerate(txt[j::4])) for j in range(4)]

NEST = [
    ("nest-terrace", "Терасата в градината", "The garden terrace", "g-a", 1000, 750),
    ("hero", "Барът", "The bar", "g-b", 1600, 1200),
    ("nest-interior", "Залата", "Inside", "g-c", 1000, 1333),
    ("nest-portion", "Пилешка порция", "Chicken bowl", "g-d", 1000, 1333),
    ("nest-exterior", "Входът", "The entrance", "g-e", 1000, 750),
    ("nest-frappe", "Кафе на терасата", "Coffee on the terrace", "g-f", 1000, 1333),
    ("nest-door", "Порция за из път", "A bowl to go", "g-g", 1000, 1333),
    ("nest-dessert", "Протеинов десерт", "Protein dessert", "g-h", 1000, 1333),
    ("nest-sandwich", "Бриош сандвич", "Brioche sandwich", "g-i", 1000, 1333),
]
gal = ""
for i, (img, cap, cen, cls, w, h) in enumerate(NEST):
    full = "images/hero-2000.webp" if img == "hero" else f"images/{img}-1600.webp"
    gal += f'          <button class="g {cls}" data-reveal="up" data-full="{full}" aria-label="{cap}">{photo(img, "(min-width: 960px) 420px, 50vw", cap, w, h)}</button>\n'

FAQ = [
    ("Къде се намира Kiwi's?", "Where is Kiwi's?", "На ул. „Никола Карев“ 14 в Пловдив. Имаме зала и тераса в градината.", "At 14 Nikola Karev St., Plovdiv, with an indoor room and a garden terrace."),
    ("Какво е работното време?", "What are the opening hours?", "Понеделник – събота, 09:00 – 21:30. В неделя почиваме.", "Monday – Saturday, 09:00 – 21:30. Closed on Sundays."),
    ("Имате ли доставка?", "Do you deliver?", "Да — през Glovo в Пловдив. За взимане на място можете да поръчате на +359 892 632 470.", "Yes — through Glovo in Plovdiv. For pick-up, call +359 892 632 470."),
    ("Колко протеин има в ястията?", "How much protein is in the dishes?", "Протеиновите порции са между 29 и 60 г протеин, бриош сандвичите между 28 и 55 г, салатите между 19 и 44 г. В менюто до всяко ястие има приблизителни калории, протеин, въглехидрати и мазнини.", "Protein bowls have 29–60 g of protein, brioche sandwiches 28–55 g, salads 19–44 g. Every item in the menu lists approximate calories, protein, carbs and fat."),
    ("Имате ли вегетариански ястия?", "Do you have vegetarian options?", "Да — вегетарианска порция, вегетариански бриош и вегетарианска салата, както и протеиновите десерти.", "Yes — a vegetarian bowl, vegetarian brioche and vegetarian salad, plus the protein desserts."),
    ("Какви са цените?", "What are the prices?", "Кафе от 2,20 €, Cloud Foam и протеинови десерти по 5 €, бриош сандвичи от 6 до 7,50 €, протеинови порции от 9 до 12 €.", "Coffee from €2.20, Cloud Foam and protein desserts €5, brioche sandwiches €6–7.50, protein bowls €9–12."),
]
faq = "".join(f'''        <details class="faq-item" data-reveal="up"><summary data-en="{qe}">{q}</summary><p data-en="{ae}">{a}</p></details>
''' for q, qe, a, ae in FAQ)
faq_ld = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, _, a, _ in FAQ]}, ensure_ascii=False, indent=2)

ARTS = [
    ("blog/kolko-protein-na-den.html", "Колко протеин ти трябва на ден?", "How much protein do you need a day?", "article-protein", 1200, "6"),
    ("blog/makrosi-za-nachinaeshti.html", "Макроси за начинаещи", "Macros for beginners", "article-macros", 1200, "5"),
    ("blog/zdravoslovno-hranene-navan.html", "Как да се храниш здравословно, когато ядеш навън", "Eating well when you eat out", "article-eatout", 1200, "5"),
]
arts = "".join(f'''        <a class="art-card" href="{h}" data-reveal="up"><div class="art-img">{photo(img, "(min-width: 960px) 360px, 90vw", "", 1600, ih)}</div><span class="art-meta">{m} <span data-en="min read">мин четене</span></span><h3 data-en="{te}">{t}</h3></a>
''' for h, t, te, img, ih, m in ARTS)

chicken = ITEMS["Пилешка порция"]

PRAISED_HEAD = ('<div class="sec-head praised-head" data-reveal="up"><div><span class="kicker" data-en="From our reviews">От отзивите</span>'
                '<h2 data-en="The dishes our guests write about.">Ястията, за които пишат гостите ни.</h2></div></div>')

# --- lunch for the office: real dishes and prices from the menu ---
def lo(cid):
    return min(float(i["price"]) for c in cats if c["id"] == cid for i in c["items"])
OFFICE = [("portion", "chicken-portion-1", "Протеинови порции", "Protein bowls", "Басмати ориз, месо или риба и зеленчуци", "Basmati rice, meat or fish and vegetables"),
          ("salad", "salmon-salad-1", "Салати", "Salads", "Големи салати с протеинов дресинг", "Big salads with a protein dressing"),
          ("sandwich", "turkey-brioche-2", "Бриош сандвичи", "Brioche sandwiches", "Протеинов бриош, изпечен при нас", "Protein brioche baked in-house")]
office = "".join(f'''          <a class="of-card" href="menu.html#{cid}" data-reveal="up">
            <span class="of-img"><img src="images/cut/{img}-500.webp" width="500" height="500" alt="" loading="lazy" decoding="async"></span>
            <b data-en="{en}">{bg}</b><span data-en="{den}">{dbg}</span>
            <em data-en="from {price_en(lo(cid))}">от {price_bg(lo(cid))}</em>
          </a>
''' for cid, img, bg, en, dbg, den in OFFICE)

body = f'''<body>
  <script src="js/preloader.js"></script>
{nav("home")}
  <main id="main">

  <section class="hero" id="hero">
    <div class="hero-bg">
      <picture><source type="image/webp" srcset="images/hero-800.webp 800w, images/hero-1400.webp 1400w, images/hero-2000.webp 2000w" sizes="100vw"><img src="images/hero.jpg" width="1600" height="1200" alt="Барът на Kiwi's в Пловдив" class="hero-bg-img" fetchpriority="high"></picture>
      <div class="hero-overlay"></div>
    </div>
    <div class="hero-content">
      <a href="#reviews" class="hero-rating"><span class="hr-stars">{STAR * 5}</span><b>5,0</b><span data-en="49 reviews on Google">49 отзива в Google</span></a>
      <h1 class="hero-h1" data-en="Healthy &amp;<br>Delicious">Здравословно &amp;<br>Вкусно</h1>
      <div class="hero-btns">
        <a href="menu.html" class="btn btn--glovo btn--lg" data-en="View the menu">Виж менюто</a>
      </div>
    </div>
    <a href="#praised" class="hero-scroll" aria-label="Надолу"><i></i></a>
  </section>

  <section class="sec praised" id="praised">
    {viewer("pv-praised", praised, scroll=True, show_menu_link=True, loop=True, bare=True, extra_cls="pv--sun", head=PRAISED_HEAD, steps=2, glovo=False)}
  </section>

  <section class="sec reviews" id="reviews">
    <div class="container rv-top">
      <div data-reveal="left"><span class="kicker" data-en="Google reviews">Отзиви в Google</span><h2 data-en="5.0 from 49 reviews.">5,0 от 49 отзива.</h2></div>
      <a href="{GMAP}" class="rv-score" target="_blank" rel="noopener" data-reveal="right"><span class="rv-score-stars">{STAR * 5}</span><span data-en="Read them on Google">Прочети ги в Google</span></a>
    </div>
    <div class="mq" aria-label="Откъси от отзиви">
      {"".join(f'<div class="mq-row"><div class="mq-track">{r}{r}{r}</div></div>' for r in ROWS)}
    </div>
    <div class="container">
      <div class="rv-grid" id="rvGrid" hidden>
{reviews}
      </div>
      <div class="rv-actions">
        <button class="btn btn--line" id="rvMore" data-en="Show all 49 reviews">Покажи всички 49 отзива</button>
        <a href="{GMAP}" class="btn btn--dark" target="_blank" rel="noopener" data-en="Leave a review">Остави отзив</a>
      </div>
      <p class="rv-note" data-en="Reviews from Google Maps; names shortened.">Отзиви от Google Карти; имената са съкратени.</p>
    </div>
  </section>

  <section class="sec office" id="office">
    <div class="container office-grid">
      <div class="office-copy" data-reveal="left">
        <span class="kicker" data-en="Kiwi's for the office">Kiwi's за офиса</span>
        <h2 data-en="A tasty lunch<br>for the whole team.">Вкусен обяд<br>за целия екип.</h2>
        <p data-en="Protein bowls, salads and brioche sandwiches — every dish with its calories and macros. Pick from the menu and order for the office, or call us and pick the order up.">Протеинови порции, салати и бриош сандвичи — всяко ястие с калории и макроси. Избери от менюто и поръчай за офиса или ни се обади и вземи поръчката от място.</p>
        <div class="office-btns">
          <a class="btn btn--glovo" href="menu.html" data-en="View the menu">Виж менюто</a>
          <a class="btn btn--dark" href="tel:+359892632470">{CALL}<span>+359 892 632 470</span></a>
        </div>
      </div>
      <div class="office-cards">
{office}      </div>
    </div>
  </section>

  <section class="sec label-sec" id="macros">
    <div class="container label-grid">
      <div class="label-copy" data-reveal="left">
        <span class="kicker" data-en="Know what you eat">Знаеш какво ядеш</span>
        <h2 data-en="Every dish comes<br>with its numbers.">Всяко ястие идва<br>със своите числа.</h2>
        <p data-en="The menu lists approximate calories, protein, carbs and fat for every dish, calculated from our recipes.">В менюто до всяко ястие има приблизителни калории, протеин, въглехидрати и мазнини, изчислени по рецептите ни.</p>
        <a href="menu.html" class="btn btn--dark" data-en="Open the menu">Отвори менюто</a>
      </div>
      <div class="nlabel" data-reveal="right" aria-label="Хранителни стойности: Пилешка порция">
        <img class="nlabel-img" src="images/cut/chicken-portion-1-500.webp" alt="" width="500" height="500" loading="lazy">
        <h3 data-en="Nutrition facts">Хранителни стойности</h3>
        <p class="nl-item">Пилешка порция · {chicken["w"]}</p>
        <div class="nl-row nl-big"><span data-en="Calories">Калории</span><b data-count="{chicken["k"]}">{chicken["k"]}</b></div>
        <div class="nl-row"><span data-en="Protein">Протеин</span><b><span data-count="{chicken["p"]}">{chicken["p"]}</span> г</b></div>
        <div class="nl-row"><span data-en="Carbohydrates">Въглехидрати</span><b><span data-count="{chicken["c"]}">{chicken["c"]}</span> г</b></div>
        <div class="nl-row"><span data-en="Fat">Мазнини</span><b><span data-count="{chicken["f"]}">{chicken["f"]}</span> г</b></div>
        <p class="nl-note" data-en="Approximate values, calculated from the recipe.">Приблизителни стойности, изчислени по рецептата.</p>
      </div>
    </div>
  </section>

  <section class="sec cats" id="categories">
    <div class="container">
      <div class="sec-head">
        <div data-reveal="left"><span class="kicker" data-en="The menu">Менюто</span><h2 data-en="What's on the menu.">Какво има в менюто.</h2></div>
        <a href="menu.html" class="sec-link" data-reveal="right" data-en="Full menu &rarr;">Цялото меню &rarr;</a>
      </div>
      <div class="ct-grid">
{cat_html}      </div>
    </div>
  </section>

  <section class="sec nest" id="nest">
    <div class="container">
      <div class="sec-head">
        <div data-reveal="left"><span class="kicker" data-en="Our nest">Нашето гнездо</span><h2 data-en="Stay for a coffee.<br>Or lunch in the garden.">Остани за кафе.<br>Или за обяд в градината.</h2></div>
      </div>
      <div class="gallery" id="gallery">
{gal}      </div>
    </div>
  </section>

  <section class="sec insta" id="instagram">
    <div class="container insta-inner" data-reveal="up">
      <a class="insta-icon" href="{IG}" target="_blank" rel="noopener" aria-label="Instagram @kiwis.bg">{IG_ICON.replace('width="18" height="18"', 'width="34" height="34"')}</a>
      <div class="insta-copy">
        <span class="kicker" data-en="Instagram">Instagram</span>
        <h2 data-en="Follow us<br>@kiwis.bg">Последвай ни<br>@kiwis.bg</h2>
        <p data-en="New drinks, dishes of the day and what's happening at Kiwi's.">Нови напитки, ястия и какво се случва в Kiwi's.</p>
      </div>
      <a class="btn btn--glovo btn--lg insta-btn" href="{IG}" target="_blank" rel="noopener">{IG_ICON}<span data-en="Follow on Instagram">Последвай в Instagram</span></a>
    </div>
  </section>

  <section class="sec faq" id="faq">
    <div class="container faq-grid">
      <div data-reveal="left"><span class="kicker" data-en="Questions">Въпроси</span><h2 data-en="Good to know.">Добре е да знаеш.</h2></div>
      <div class="faq-list">
{faq}      </div>
    </div>
  </section>

  <section class="sec articles" id="articles">
    <div class="container">
      <div class="sec-head">
        <div data-reveal="left"><span class="kicker" data-en="Articles">Статии</span><h2 data-en="Eat smarter.">Храни се по-умно.</h2></div>
        <a href="blog/" class="sec-link" data-reveal="right" data-en="All articles &rarr;">Всички статии &rarr;</a>
      </div>
      <div class="art-grid">
{arts}      </div>
    </div>
  </section>

  <section class="sec about" id="about">
    <div class="blob blob--a" data-speed="-0.12" aria-hidden="true"></div>
    <div class="container about-grid">
      <div class="about-text" data-reveal="left">
        <span class="kicker" data-en="About Kiwi's">За Kiwi's</span>
        <h2 data-en="Food that<br><em>fuels you.</em>">Храна, която те<br><em>зарежда.</em></h2>
        <p data-en="Kiwi's is a café for healthy food at 14 Nikola Karev St. in Plovdiv: brioche sandwiches, bowls with basmati rice, salads, protein desserts, Cloud Foam drinks and coffee.">Kiwi's е място за здравословна храна и кафе на ул. „Никола Карев“ 14 в Пловдив: сандвичи в протеинов бриош, порции с басмати ориз, салати, протеинови десерти, Cloud Foam напитки и кафе.</p>
        <p data-en="The menu lists calories, protein, carbs and fat for every dish. You can eat in the room or in the garden, take it with you, or order on Glovo.">В менюто до всяко ястие са дадени калории, протеин, въглехидрати и мазнини. Можеш да хапнеш в залата или в градината, да вземеш за из път или да поръчаш през Glovo.</p>
        <div class="about-stats">
          <div><b data-count="49">49</b><span data-en="Google reviews">отзива в Google</span></div>
          <div><b>5,0</b><span data-en="average rating">средна оценка</span></div>
          <div><b data-en="Mon–Sat">Пон–Съб</b><span>09:00 – 21:30</span></div>
        </div>
      </div>
      <div class="about-img" data-reveal="right">
        {photo("nest-portion", "(min-width: 960px) 460px, 100vw", "Пилешка порция в Kiwi's пред стената с логото")}
      </div>
    </div>
  </section>

  <section class="sec visit" id="visit">
    <div class="container visit-grid">
      <div class="visit-info h-card" data-reveal="left">
        <span class="kicker" data-en="Contact">Контакти</span>
        <h2 data-en="Come say hello.">Заповядай при нас.</h2>
        <ul class="visit-list">
          <li><b data-en="Address">Адрес</b><span class="p-adr h-adr"><span class="p-name" hidden>Kiwi's</span><span class="p-street-address" data-en="14 Nikola Karev St.">ул. „Никола Карев“ 14</span>, <span class="p-locality" data-en="Plovdiv">Пловдив</span><span class="p-country-name" hidden>България</span></span></li>
          <li><b data-en="Hours">Работно време</b><span data-en="Mon — Sat, 09:00 — 21:30 · Sunday closed">Пон — Съб, 09:00 — 21:30 · неделя почивен ден</span></li>
          <li><b data-en="Phone">Телефон</b><span><a class="p-tel" href="tel:+359892632470">+359 892 632 470</a></span></li>
          <li><b>Instagram</b><span><a class="vl-ig" href="{IG}" target="_blank" rel="noopener">{IG_ICON}@kiwis.bg</a></span></li>
          <li><b data-en="Delivery">Доставка</b><span><a href="{GLOVO}" target="_blank" rel="noopener">Glovo</a> <span data-en="in Plovdiv">в Пловдив</span></span></li>
        </ul>
        <div class="visit-btns">
          <a href="{DIR}" class="btn btn--dark" target="_blank" rel="noopener" data-en="Get directions">Упътване</a>
          <a href="{GLOVO}" class="btn btn--glovo" target="_blank" rel="noopener">{BIKE}<span data-en="Glovo delivery">Доставка с Glovo</span></a>
        </div>
      </div>
      <div class="visit-map" data-reveal="right">
        <iframe src="https://maps.google.com/maps?q=Kiwi%27s%2C%20%D1%83%D0%BB.%20%D0%9D%D0%B8%D0%BA%D0%BE%D0%BB%D0%B0%20%D0%9A%D0%B0%D1%80%D0%B5%D0%B2%2014%2C%20%D0%9F%D0%BB%D0%BE%D0%B2%D0%B4%D0%B8%D0%B2&amp;z=16&amp;output=embed" width="100%" height="100%" style="border:0" loading="lazy" allowfullscreen title="Kiwi's на картата — ул. Никола Карев 14, Пловдив" referrerpolicy="no-referrer-when-downgrade"></iframe>
      </div>
    </div>
  </section>

  </main>

{footer("home")}

  <div class="lb" id="lb" role="dialog" aria-modal="true" aria-label="Снимки" hidden>
    <button class="lb-x" id="lbX" aria-label="Затвори">&times;</button>
    <button class="lb-nav lb-prev" id="lbPrev" aria-label="Предишна">&lsaquo;</button>
    <figure><img id="lbImg" alt=""><figcaption id="lbCap"></figcaption></figure>
    <button class="lb-nav lb-next" id="lbNext" aria-label="Следваща">&rsaquo;</button>
  </div>

{sticky_order()}

  <script src="js/pv.js"></script>
  <script src="js/main.js"></script>
  <script src="js/join.js" defer></script>
</body>
</html>
'''
if "FAQPage" not in head:
    head = head.replace("</head>", f'  <script type="application/ld+json">\n{faq_ld}\n  </script>\n</head>')
open(OUT, "w", encoding="utf-8").write(head + body)
print("index ok")
