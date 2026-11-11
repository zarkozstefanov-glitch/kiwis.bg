"""Shared markup for the product viewer: green podium on one side, product info on the other."""
import html as H
from pathlib import Path

CUT = Path("/Users/zarko.stefanov/Kivi's/website/images/cut")
GLOVO = "https://glovoapp.com/bg/bg/plovdiv/stores/kiwis-pdv"


def e(s):
    return H.escape(s, quote=True)


def price_bg(x):
    return f"{float(x):.2f}".replace(".", ",") + " €"


def price_en(x):
    return f"€{float(x):.2f}"


def shots(img):
    if not img:
        return 0
    return 2 if (CUT / f"{img}-2-500.webp").exists() else 1


def macro_bar(label_bg, label_en, val, unit, maxv, cls):
    pct = min(100, round(val / maxv * 100))
    return (f'<div class="pv-m {cls}"><dt data-en="{label_en}">{label_bg}</dt>'
            f'<dd><b>{val}</b>{unit}</dd><i style="--v:{pct}%"></i></div>')


def viewer(vid, items, prefix="", scroll=False, show_menu_link=False, heading_level="h3", loop=False, bare=False, head="", extra_cls="", steps=None, glovo=True):
    """items: dicts with img, bg, en, dbg, den, w, price, k, p, c, f, badge, badge_en, quote?, quote_by?"""
    n = len(items)
    figs, panels, thumbs = "", "", ""
    for i, it in enumerate(items):
        img = it.get("img")
        ns = shots(img)
        if img:
            # sandwiches: the side shot (filling visible) is the main photo, the box shot is the second
            a, b = (2, 1) if ("brioche" in img and ns > 1) else (1, 2)
            src = f"{prefix}images/cut/{img}-{a}-900.webp"
            srcset = f"{prefix}images/cut/{img}-{a}-500.webp 500w, {prefix}images/cut/{img}-{a}-900.webp 900w"
            alt2 = f' data-alt="{prefix}images/cut/{img}-{b}-900.webp"' if ns > 1 else ""
            lazy = "" if i == 0 else ' loading="lazy"'
            flat = " pv-item--flat" if ("portion" in img or "salad" in img) else ""
            figs += (f'<figure class="pv-item{flat}" data-i="{i}"><img class="pv-img" src="{src}" srcset="{srcset}" '
                     f'sizes="(min-width: 960px) 460px, 70vw" width="900" height="900" alt="{e(it["bg"])}" decoding="async"{lazy}{alt2}>'
                     f'<img class="pv-refl" src="{prefix}images/cut/{img}-{a}-500.webp" alt="" aria-hidden="true" decoding="async"{lazy}></figure>')
            th = f'<img src="{prefix}images/cut/{img}-{a}-500.webp" alt="" width="80" height="80" decoding="async">'
        else:
            figs += (f'<figure class="pv-item pv-item--soon" data-i="{i}"><span class="pv-soon">'
                     f'<img src="{prefix}images/kiwi-icon.jpg" alt="" width="72" height="72"><b data-en="Photo coming soon">Снимка очаквайте скоро</b></span></figure>')
            th = f'<span class="pv-th-ph"><img src="{prefix}images/kiwi-icon.jpg" alt="" width="40" height="40" loading="lazy"></span>'
        badge = f'<span class="pv-badge" data-en="{e(it.get("badge_en", ""))}">{e(it["badge"])}</span>' if it.get("badge") else ""
        quote = ""
        if it.get("quote"):
            quote = (f'<blockquote class="pv-quote"><p>„{e(it["quote"])}“</p>'
                     f'<cite>— {e(it["quote_by"])}, <span data-en="Google review">отзив в Google</span></cite></blockquote>')
        weight = f'<span class="pv-w">{e(it["w"])}</span>' if it.get("w") else ""
        glovo_btn = (f'<a class="btn btn--glovo" href="{GLOVO}" target="_blank" rel="noopener" data-en="Order on Glovo">Поръчай в Glovo</a>' if glovo else "")
        menu_link = (f'<a class="btn btn--line pv-more" href="{prefix}menu.html#{it["cat"]}" data-en="See in menu">Виж в менюто</a>'
                     if show_menu_link and it.get("cat") else "")
        panels += f'''<article class="pv-panel{' is-on' if i == 0 else ''}" data-i="{i}" id="{vid}-{i}"{'' if i == 0 else ' aria-hidden="true"'}>
          <div class="pv-meta"><span class="pv-num">{i + 1:02d}<small> / {n:02d}</small></span>{badge}</div>
          <{heading_level} class="pv-name" data-en="{e(it["en"])}">{e(it["bg"])}</{heading_level}>
          <p class="pv-desc" data-en="{e(it["den"])}">{e(it["dbg"])}</p>
          {quote}
          <dl class="pv-macros" aria-label="Приблизителни хранителни стойности">
            {macro_bar("Калории", "Calories", it["k"], " kcal", 900, "pv-m--k")}
            {macro_bar("Протеин", "Protein", it["p"], " г", 60, "pv-m--p")}
            {macro_bar("Въглехидрати", "Carbs", it["c"], " г", 80, "pv-m--c")}
            {macro_bar("Мазнини", "Fat", it["f"], " г", 45, "pv-m--f")}
          </dl>
          <div class="pv-buy"><span class="pv-price" data-en="{price_en(it["price"])}">{price_bg(it["price"])}</span>{weight}
            <div class="pv-ctas">{menu_link}{glovo_btn}</div></div>
        </article>
'''
        thumbs += (f'<button class="pv-th{" is-on" if i == 0 else ""}" data-i="{i}" role="tab" aria-selected="{"true" if i == 0 else "false"}" '
                   f'aria-controls="{vid}-{i}" aria-label="{e(it["bg"])}">{th}</button>')
    turn = ('<button class="pv-turn" type="button" aria-label="Виж другата снимка" title="Друга снимка">'
            '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            '<rect x="3" y="5" width="15" height="13" rx="2"/><path d="M7 3h12a2 2 0 012 2v10"/><circle cx="8.5" cy="10" r="1.6"/><path d="M18 15l-4.5-4.5L5 18"/></svg>'
            '<span class="pv-turn-n">1/2</span></button>')
    cls = "pv" + (" pv--bare" if bare else "") + (" " + extra_cls if extra_cls else "")
    core = f'''<div class="{cls}" id="{vid}" data-pv{' data-scroll' if scroll else ''}{' data-loop' if loop else ''} tabindex="0" style="--n:{n}">
      <div class="pv-stage">
        <div class="pv-light" aria-hidden="true"></div>
        <svg class="pv-lines" viewBox="0 0 400 400" aria-hidden="true"><circle cx="200" cy="200" r="150"/><circle cx="200" cy="200" r="178"/><circle cx="200" cy="200" r="196"/></svg>
        <div class="pv-podium" aria-hidden="true"><div class="pd-glow"></div><div class="pd-side"></div><div class="pd-top"><i class="pd-sheen"></i><i class="pd-ring"></i></div></div>
        <div class="pv-items">{figs}</div>
        <button class="pv-arrow pv-prev" type="button" aria-label="Предишно">&#8249;</button>
        <button class="pv-arrow pv-next" type="button" aria-label="Следващо">&#8250;</button>
        {turn}
        <div class="pv-dots" aria-hidden="true">{"<i></i>" * n}</div>
      </div>
      <div class="pv-side">
        <div class="pv-panels">
{panels}        </div>
        <div class="pv-thumbs" role="tablist" aria-label="Избери">{thumbs}</div>
      </div>
    </div>'''
    if scroll:
        st = steps if steps is not None else n
        return f'<div class="pv-scroll" data-steps="{st}" style="--n:{n};--steps:{st}"><div class="pv-sticky"><div class="container">{head}{core}</div></div></div>'
    return core


# ---------------------------------------------------------------- shared chrome
BIKE = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 17h-2v-6l2-5h9l4 5h1a2 2 0 012 2v4h-2"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/><path d="M9 17h6"/></svg>'
CALL = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.86 19.86 0 01-8.63-3.07 19.5 19.5 0 01-6-6 19.86 19.86 0 01-3.07-8.67A2 2 0 014.11 2h3a2 2 0 012 1.72c.12.96.36 1.9.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.91.34 1.85.58 2.81.7A2 2 0 0122 16.92z"/></svg>'
GMAP = "https://www.google.com/maps?cid=1892105797985093642"
IG = "https://www.instagram.com/kiwis.bg/"
IG_ICON = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2.5" y="2.5" width="19" height="19" rx="5.5"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.6" cy="6.4" r="1.1" fill="currentColor" stroke="none"/></svg>'


def links(page):
    """page: 'home' | 'menu' | 'blog'. Returns (href for home, list of nav links)."""
    if page == "home":
        h, a = "#", lambda x: "#" + x
        m, b, img = "menu.html", "blog/", "images/"
    elif page == "menu":
        h, a = "index.html", lambda x: "index.html#" + x
        m, b, img = "menu.html", "blog/", "images/"
    else:
        h, a = "/", lambda x: "/#" + x
        m, b, img = "/menu.html", "/blog/", "/images/"
    # "Меню" is the last link, right next to the language switch and the order button
    L = [(a("about"), "За нас", "About", ""), (a("reviews"), "Отзиви", "Reviews", ""), (b, "Статии", "Articles", "blog"),
         (a("visit"), "Контакти", "Contact", ""), (m, "Меню", "Menu", "menu")]
    return h, L, img


def nav(page):
    home, L, img = links(page)
    items = "".join(f'<a href="{u}" data-en="{en}"{" aria-current=\"page\" class=\"is-current\"" if k and k == page else ""}>{bg}</a>' for u, bg, en, k in L)
    if page == "home":   # on the landing page every button leads to the menu; ordering happens from there
        cta = f'<a href="menu.html" class="nav-cta"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h10"/></svg><span data-en="Menu">Меню</span></a>'
        mm_cta = '<a href="menu.html" class="btn btn--glovo btn--lg mm-cta" data-en="View the menu">Виж менюто</a>'
    else:
        cta = f'<a href="{GLOVO}" class="nav-cta" target="_blank" rel="noopener">{BIKE}<span data-en="Order">Поръчай</span></a>'
        mm_cta = f'<a href="{GLOVO}" class="btn btn--glovo btn--lg mm-cta" target="_blank" rel="noopener">{BIKE}<span data-en="Order on Glovo">Поръчай в Glovo</span></a>'
    mm = "".join(f'<a href="{u}" class="mm-link" data-en="{en}">{bg}</a>' for u, bg, en, k in L)
    return f'''  <a class="skip" href="#main" data-en="Skip to content">Към съдържанието</a>
  <header class="nav" id="nav">
    <div class="nav-bar">
      <a href="{home}" class="nav-logo" aria-label="Kiwi's — начало"><img src="{img}kiwi-icon.jpg" alt="" width="38" height="38"><span class="nav-brand">KiWi'S</span></a>
      <nav class="nav-links" aria-label="Основна навигация">{items}</nav>
      <div class="nav-right">
        <div class="lang-toggle"><button class="lang-btn is-active" data-lang="bg" aria-label="Български">BG</button><button class="lang-btn" data-lang="en" aria-label="English">EN</button></div>
        {cta}
        <button class="hamburger" id="hamburger" aria-label="Меню" aria-expanded="false"><span></span><span></span></button>
      </div>
    </div>
  </header>
  <div class="mobile-menu" id="mobileMenu" aria-hidden="true">
    <div class="mm-inner">
      {mm}
      {mm_cta}
      <p class="mm-info"><span data-en="Mon — Sat, 09:00 — 21:30">Пон — Съб, 09:00 — 21:30</span><br><a href="tel:+359892632470">+359 892 632 470</a></p>
      <a href="{IG}" class="mm-ig" target="_blank" rel="noopener">{IG_ICON}<span>@kiwis.bg</span></a>
    </div>
  </div>
'''


def footer(page):
    home, L, img = links(page)
    m = next(u for u, _, _, k in L if k == "menu"); b = next(u for u, _, _, k in L if k == "blog")
    return f'''  <footer class="footer">
    <div class="container footer-inner">
      <div class="footer-brand"><img src="{img}kiwi-icon.jpg" alt="" width="40" height="40"><div><strong>KiWi'S</strong><span data-en="14 Nikola Karev St., Plovdiv · Mon–Sat 09:00–21:30">ул. „Никола Карев“ 14, Пловдив · Пон–Съб 09:00–21:30</span></div></div>
      <nav class="footer-links" aria-label="Footer">
        <a href="{m}" data-en="Menu">Меню</a><a href="{b}" data-en="Articles">Статии</a>
        <a href="{GLOVO}" target="_blank" rel="noopener">Glovo</a>
        <a href="{GMAP}" target="_blank" rel="noopener" data-en="Google reviews">Отзиви в Google</a>
        <a href="{IG}" target="_blank" rel="noopener" class="ft-ig">{IG_ICON}<span>Instagram</span></a>
        <a href="tel:+359892632470">+359 892 632 470</a>
        <a href="/privacy.html" data-en="Privacy">Поверителност</a>
      </nav>
      <p class="footer-copy">&copy; 2026 KiWi'S</p>
    </div>
  </footer>
'''


def sticky_order():
    return f'''  <div class="sticky-order" id="stickyOrder">
    <a href="{GLOVO}" class="so-btn so-btn--glovo" target="_blank" rel="noopener">{BIKE}<span data-en="Order on Glovo">Поръчай в Glovo</span></a>
    <a href="tel:+359892632470" class="so-btn so-btn--call" aria-label="Обади се">{CALL}</a>
  </div>
'''
