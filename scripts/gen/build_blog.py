import os, sys, json, html as H
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from pv_lib import nav, footer
OUT = sys.argv[1]  # website/blog
os.makedirs(OUT, exist_ok=True)
GLOVO = "https://glovoapp.com/bg/bg/plovdiv/stores/kiwis-pdv"
TODAY = "2026-11-11"

ARTICLES = [
 {
  "slug": "kolko-protein-na-den",
  "title": "Колко протеин ти трябва на ден?",
  "desc": "Колко протеин на ден е нужен на възрастен, на човек, който тренира, и след 65 години — с препоръките на EFSA и ISSN и примери с реални ястия.",
  "img": "nest-portion", "w": 1000, "h": 1333, "mins": 6,
  "body": """
<p class="lead">Протеинът е навсякъде — в рекламите, във фитнеса, в менютата. Но колко всъщност ти трябва? Отговорът зависи от теглото ти, от това колко се движиш и от възрастта ти.</p>

<h2>Основната препоръка за възрастни</h2>
<p>Европейският орган за безопасност на храните (EFSA) дава референтен прием от <strong>0,83 г протеин на килограм телесно тегло на ден</strong> за здрави възрастни. Това е количеството, което покрива нуждите на почти всички хора, които не тренират активно.</p>
<p>За човек с 70 кг това са около <strong>58 г протеин на ден</strong>.</p>

<h2>Ако тренираш</h2>
<p>Международното дружество по спортно хранене (ISSN) препоръчва <strong>1,4 – 2,0 г/кг на ден</strong> за повечето хора, които тренират редовно — особено ако целта е мускулна маса. За същия човек със 70 кг това са <strong>около 98 – 140 г</strong> на ден.</p>
<p>ISSN съветва количеството да се разпредели в няколко хранения — приблизително <strong>20 – 40 г протеин на хранене</strong> (около 0,25 – 0,4 г/кг), на всеки 3 – 4 часа.</p>

<h2>След 65 години</h2>
<p>С възрастта мускулите реагират по-слабо на протеина. Експертната група PROT-AGE препоръчва <strong>1,0 – 1,2 г/кг на ден</strong> за здрави хора над 65 години и повече при активни хора.</p>

<h2>Набързо: колко е за мен?</h2>
<div class="tbl"><table>
<thead><tr><th>Тегло</th><th>Не тренирам (0,83 г/кг)</th><th>Тренирам (1,4 – 2,0 г/кг)</th></tr></thead>
<tbody>
<tr><td>55 кг</td><td>~46 г</td><td>77 – 110 г</td></tr>
<tr><td>70 кг</td><td>~58 г</td><td>98 – 140 г</td></tr>
<tr><td>85 кг</td><td>~71 г</td><td>119 – 170 г</td></tr>
</tbody></table></div>

<h2>Как изглежда това в чинията</h2>
<p>Едно хранене с 30 – 45 г протеин те води доста напред. В <a href="/menu.html">менюто на Kiwi's</a> всяко ястие е с приблизителни макроси — например пилешката порция е около 60 г протеин, салата Цезар около 44 г, а протеиновите десерти в кен около 20 – 22 г.</p>

<div class="note"><strong>Важно:</strong> това е обща информация, не медицински съвет. Ако имаш бъбречно заболяване, си бременна или имаш специфичен здравословен проблем, консултирай се с лекар или диетолог.</div>
""",
  "sources": [
   ("EFSA — Scientific Opinion on Dietary Reference Values for protein (2012)", "https://www.efsa.europa.eu/en/efsajournal/pub/2557"),
   ("Jäger et al. — ISSN Position Stand: Protein and Exercise (2017)", "https://jissn.biomedcentral.com/articles/10.1186/s12970-017-0177-8"),
   ("Bauer et al. — PROT-AGE recommendations for older people (2013)", "https://doi.org/10.1016/j.jamda.2013.05.021"),
  ],
 },
 {
  "slug": "makrosi-za-nachinaeshti",
  "title": "Макроси за начинаещи: калории, протеин, въглехидрати, мазнини",
  "desc": "Какво са макросите, колко калории има в грам протеин, въглехидрати и мазнини, и как да четеш хранителните стойности в менюто.",
  "img": "nest-dessert", "w": 1000, "h": 1333, "mins": 5,
  "body": """
<p class="lead">„Макроси“ са трите големи групи хранителни вещества, от които идва енергията в храната: <strong>протеини, въглехидрати и мазнини</strong>. Ако ги разбираш, разбираш и етикета, и менюто.</p>

<h2>Колко калории има в един грам</h2>
<div class="tbl"><table>
<thead><tr><th>Макрос</th><th>kcal на грам</th><th>За какво служи</th></tr></thead>
<tbody>
<tr><td>Протеин</td><td>4</td><td>Мускули, засищане, възстановяване</td></tr>
<tr><td>Въглехидрати</td><td>4</td><td>Бърза енергия за мозъка и мускулите</td></tr>
<tr><td>Мазнини</td><td>9</td><td>Хормони, усвояване на витамини A, D, E, K</td></tr>
</tbody></table></div>
<p>Затова мазнините „натежават“ в калориите най-бързо — грам мазнина носи над два пъти повече енергия от грам протеин.</p>

<h2>Пример с реално ястие</h2>
<p>Салата Цезар в Kiwi's е около <strong>44 г протеин, 22 г въглехидрати и 15 г мазнини</strong>:</p>
<p class="calc">44 × 4 + 22 × 4 + 15 × 9 = 176 + 88 + 135 = <strong>≈ 400 kcal</strong></p>
<p>Точно това пише и в менюто. Сметката никога не е до калория точна — фибрите, закръгляването и естествените разлики в продуктите дават малки отклонения, затова стойностите са „приблизителни“.</p>

<h2>Каква част от калориите от какво?</h2>
<p>Американският институт по медицина дава широки граници за възрастни (като дял от дневните калории):</p>
<ul>
<li><strong>Въглехидрати:</strong> 45 – 65 %</li>
<li><strong>Мазнини:</strong> 20 – 35 %</li>
<li><strong>Протеин:</strong> 10 – 35 %</li>
</ul>
<p>Световната здравна организация допълва: свободните захари да са под 10 % от калориите, а наситените мазнини — също под 10 %.</p>

<h2>Как да ползваш това на практика</h2>
<ul>
<li>Започни с протеина — той засища най-много и пази мускулите при отслабване.</li>
<li>Гледай калориите като общ бюджет за деня, не като забрана.</li>
<li>Избирай въглехидрати със сито: ориз, зеленчуци, плодове, пълнозърнести.</li>
</ul>
<p>В <a href="/menu.html">нашето меню</a> до всяко ястие има kcal, протеин, въглехидрати и мазнини, така че лесно си правиш сметката.</p>
<div class="note">Информацията е обща и не замества съвет от лекар или диетолог.</div>
""",
  "sources": [
   ("Institute of Medicine — Dietary Reference Intakes for Energy, Carbohydrate, Fiber, Fat, Fatty Acids, Cholesterol, Protein and Amino Acids (2005)", "https://nap.nationalacademies.org/catalog/10490"),
   ("WHO — Healthy diet (fact sheet)", "https://www.who.int/news-room/fact-sheets/detail/healthy-diet"),
   ("FAO — Food energy: methods of analysis and conversion factors (2003)", "https://www.fao.org/4/y5022e/y5022e00.htm"),
  ],
 },
 {
  "slug": "zdravoslovno-hranene-navan",
  "title": "Как да се храниш здравословно, когато ядеш навън",
  "desc": "Практични съвети за здравословно хранене в заведение: как да изградиш чинията, какво да внимаваш със сосовете, напитките и солта.",
  "img": "nest-terrace", "w": 1000, "h": 750, "mins": 5,
  "body": """
<p class="lead">Храненето навън не трябва да разваля режима. С няколко прости правила можеш да ядеш вкусно, да се заситиш и пак да си в целите си.</p>

<h2>1. Изгради чинията по правилото на половинките</h2>
<p>„Здравословната чиния“ на Харвардското училище по обществено здраве е лесен ориентир: <strong>половината — зеленчуци</strong> (и плодове), <strong>четвърт — качествен протеин</strong>, <strong>четвърт — пълнозърнести или сложни въглехидрати</strong>. Така работят и нашите протеинови порции: месо или риба, басмати ориз и много зеленчуци.</p>

<h2>2. Протеинът първо</h2>
<p>Ястие с 30+ г протеин държи сит по-дълго и намалява желанието за „нещо сладко“ след това. Пиле, пуйка, риба, яйца, скир и извара са добри избори.</p>

<h2>3. Внимавай със сосовете — не с храната</h2>
<p>Много калории се крият в майонезените сосове и дресингите. Помоли соса отделно и сложи колкото ти трябва. Сосовете на йогуртова основа (като скир) са по-леки.</p>

<h2>4. Пий вода, не калории</h2>
<p>Сладките газирани и шейковете могат да добавят 200 – 400 kcal към обяда. СЗО препоръчва свободните захари да са под 10 % от дневните калории — а една кутийка газирана напитка често съдържа над 30 г захар.</p>

<h2>5. Солта</h2>
<p>СЗО препоръчва <strong>под 5 г сол на ден</strong> за възрастни. В заведенията солта е по-висока — не досолявай преди да опиташ.</p>

<h2>6. Зеленчуци при всяко хранене</h2>
<p>Целта на СЗО е поне <strong>400 г плодове и зеленчуци на ден</strong>. Салата към основното или порция с много зеленчуци покриват голяма част от това.</p>

<h2>7. Знай какво ядеш</h2>
<p>Най-лесно е, когато заведението ти казва хранителните стойности. В <a href="/menu.html">менюто на Kiwi's</a> всяко ястие е с приблизителни калории и макроси.</p>
<div class="note">Информацията е обща и не замества съвет от лекар или диетолог.</div>
""",
  "sources": [
   ("Harvard T.H. Chan School of Public Health — Healthy Eating Plate", "https://nutritionsource.hsph.harvard.edu/healthy-eating-plate/"),
   ("WHO — Healthy diet (fact sheet)", "https://www.who.int/news-room/fact-sheets/detail/healthy-diet"),
   ("WHO — Salt reduction (fact sheet)", "https://www.who.int/news-room/fact-sheets/detail/salt-reduction"),
  ],
 },
]

FONT = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..900;1,9..144,300..900&family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">'


def pic(img, w, h, sizes, lazy=True):
    return (f'<picture><source type="image/webp" srcset="/images/{img}-600.webp 600w, /images/{img}-1000.webp 1000w, /images/{img}-1600.webp 1600w" sizes="{sizes}">'
            f'<img src="/images/{img}.jpg" width="{w}" height="{h}" alt=""{" loading=\"lazy\"" if lazy else ""} decoding="async"></picture>')


def shell(title, desc, canon, body, ld, og_img="/images/og-image.jpg"):
    return f'''<!DOCTYPE html>
<html lang="bg" data-lang="bg">
<head>
  <meta charset="UTF-8">
  <style>@view-transition{{navigation:auto}}</style>
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <title>{H.escape(title)}</title>
  <meta name="description" content="{H.escape(desc)}">
  <link rel="canonical" href="https://kiwis.bg{canon}">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta name="theme-color" content="#1A2D1E">
  <meta property="og:type" content="article">
  <meta property="og:site_name" content="Kiwi's">
  <meta property="og:locale" content="bg_BG">
  <meta property="og:url" content="https://kiwis.bg{canon}">
  <meta property="og:title" content="{H.escape(title)}">
  <meta property="og:description" content="{H.escape(desc)}">
  <meta property="og:image" content="https://kiwis.bg{og_img}">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" href="/favicon.ico" sizes="48x48">
  <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  {FONT}
  <link rel="stylesheet" href="/css/style.css">
  <link rel="stylesheet" href="/css/blog.css">
  <script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
  </script>
</head>
<body class="blog">
{nav("blog")}
  <main id="main">
{body}
  </main>
{footer("blog")}
  <script src="/js/main.js"></script>
</body>
</html>
'''


PUB = {"@type": "Organization", "@id": "https://kiwis.bg/#restaurant", "name": "Kiwi's", "url": "https://kiwis.bg/", "logo": {"@type": "ImageObject", "url": "https://kiwis.bg/images/logo.png"}}

for a in ARTICLES:
    canon = f"/blog/{a['slug']}.html"
    others = "".join(f'<li><a href="/blog/{o["slug"]}.html">{H.escape(o["title"])}</a></li>' for o in ARTICLES if o is not a)
    src = "".join(f'<li><a href="{u}" target="_blank" rel="noopener">{H.escape(t)}</a></li>' for t, u in a["sources"])
    body = f'''    <article class="post">
      <div class="container post-head">
        <a class="back-link" href="/" data-back aria-label="Назад"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg><span>Назад</span></a>
        <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Kiwi's</a> / <a href="/blog/">Статии</a></nav>
        <h1>{H.escape(a["title"])}</h1>
        <p class="post-meta">{a["mins"]} мин четене · Kiwi's · {TODAY[8:]}.{TODAY[5:7]}.{TODAY[:4]}</p>
      </div>
      <div class="container post-hero">{pic(a["img"], a["w"], a["h"], "(min-width: 900px) 860px, 100vw", lazy=False)}</div>
      <div class="container post-body">
{a["body"]}
        <aside class="sources"><h2>Източници</h2><ol>{src}</ol></aside>
        <div class="post-cta">
          <div><strong>Гладен ли си?</strong><span>Протеинова храна с калории и макроси на всяко ястие — ул. „Никола Карев“ 14, Пловдив.</span></div>
          <div class="post-cta-btns"><a class="btn btn--glovo" href="{GLOVO}" target="_blank" rel="noopener">Поръчай в Glovo</a><a class="btn btn--dark" href="/menu.html">Виж менюто</a></div>
        </div>
        <aside class="more"><h2>Още статии</h2><ul>{others}</ul></aside>
      </div>
    </article>'''
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "Article", "headline": a["title"], "description": a["desc"], "image": f"https://kiwis.bg/images/{a['img']}.jpg",
         "datePublished": TODAY, "dateModified": TODAY, "inLanguage": "bg", "author": PUB, "publisher": PUB,
         "mainEntityOfPage": f"https://kiwis.bg{canon}",
         "citation": [u for _, u in a["sources"]]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Kiwi's", "item": "https://kiwis.bg/"},
            {"@type": "ListItem", "position": 2, "name": "Статии", "item": "https://kiwis.bg/blog/"},
            {"@type": "ListItem", "position": 3, "name": a["title"], "item": f"https://kiwis.bg{canon}"}]}]}
    open(f"{OUT}/{a['slug']}.html", "w", encoding="utf-8").write(
        shell(f"{a['title']} | Kiwi's Пловдив", a["desc"], canon, body, ld, f"/images/{a['img']}.jpg"))

cards = "".join(f'''        <a class="art-card" href="/blog/{a["slug"]}.html">
          <div class="art-img">{pic(a["img"], a["w"], a["h"], "(min-width: 900px) 360px, 90vw")}</div>
          <span class="art-meta">{a["mins"]} мин четене</span>
          <h2>{H.escape(a["title"])}</h2>
          <p>{H.escape(a["desc"])}</p>
        </a>
''' for a in ARTICLES)
body = f'''    <section class="post">
      <div class="container post-head">
        <a class="back-link" href="/" data-back aria-label="Назад"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg><span>Назад</span></a>
        <nav class="crumbs" aria-label="Breadcrumb"><a href="/">Kiwi's</a> / Статии</nav>
        <h1>Статии за здравословно хранене</h1>
        <p class="post-meta">Протеин, макроси и как да се храниш добре — кратко, ясно и с източници.</p>
      </div>
      <div class="container art-grid blog-list">
{cards}      </div>
    </section>'''
ld = {"@context": "https://schema.org", "@type": "Blog", "name": "Статии на Kiwi's", "url": "https://kiwis.bg/blog/", "inLanguage": "bg", "publisher": PUB,
      "blogPost": [{"@type": "BlogPosting", "headline": a["title"], "url": f"https://kiwis.bg/blog/{a['slug']}.html", "datePublished": TODAY} for a in ARTICLES]}
open(f"{OUT}/index.html", "w", encoding="utf-8").write(
    shell("Статии за здравословно хранене и протеин | Kiwi's Пловдив", "Колко протеин ти трябва, какво са макросите и как да се храниш здравословно навън — статии от Kiwi's Пловдив с източници.", "/blog/", body, ld))
print("blog ok")
