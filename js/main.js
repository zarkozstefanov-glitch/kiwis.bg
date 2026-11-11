document.addEventListener('DOMContentLoaded', () => {
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // === Language ===
  function setLang(lang) {
    document.documentElement.setAttribute('data-lang', lang);
    document.documentElement.setAttribute('lang', lang);
    try { localStorage.setItem('kiwi-lang', lang); } catch (e) {}
    $$('[data-en]').forEach(el => {
      if (!el.dataset.bg) el.dataset.bg = el.innerHTML;
      el.innerHTML = lang === 'en' ? el.dataset.en : el.dataset.bg;
    });
    $$('.lang-btn').forEach(b => b.classList.toggle('is-active', b.dataset.lang === lang));
    updateOpenStatus();
    document.dispatchEvent(new CustomEvent('kiwi:lang'));
  }
  $$('.lang-btn').forEach(b => b.addEventListener('click', () => setLang(b.dataset.lang)));
  let saved = null;
  try { saved = localStorage.getItem('kiwi-lang'); } catch (e) {}
  if (saved && saved !== 'bg') setLang(saved);

  // === Open / closed (Plovdiv time, Mon–Sat 09:00–21:30) ===
  function updateOpenStatus() {
    const el = $('#openStatus');
    if (!el) return;
    let day, mins;
    try {
      const parts = new Intl.DateTimeFormat('en-GB', { timeZone: 'Europe/Sofia', weekday: 'short', hour: '2-digit', minute: '2-digit', hourCycle: 'h23' }).formatToParts(new Date());
      const get = t => parts.find(p => p.type === t).value;
      day = get('weekday'); mins = parseInt(get('hour'), 10) * 60 + parseInt(get('minute'), 10);
    } catch (e) { return; }
    const lang = document.documentElement.getAttribute('data-lang') === 'en' ? 'en' : 'bg';
    let state = day === 'Sun' ? 'sunday' : (mins >= 540 && mins < 1290 ? 'open' : 'closed');
    if (state === 'closed' && day === 'Sat' && mins >= 1290) state = 'sunday';
    el.textContent = el.dataset[lang + state[0].toUpperCase() + state.slice(1)];
    el.classList.toggle('is-open', state === 'open');
    el.classList.toggle('is-closed', state !== 'open');
  }
  updateOpenStatus();
  setInterval(updateOpenStatus, 60000);

  // === Mobile menu ===
  const burger = $('#hamburger'), mm = $('#mobileMenu');
  if (burger && mm) {
    const closeMenu = () => { mm.classList.remove('is-open'); burger.classList.remove('is-active'); burger.setAttribute('aria-expanded', 'false'); mm.setAttribute('aria-hidden', 'true'); document.body.style.overflow = ''; };
    burger.addEventListener('click', () => {
      const open = mm.classList.toggle('is-open');
      burger.classList.toggle('is-active', open);
      burger.setAttribute('aria-expanded', String(open));
      mm.setAttribute('aria-hidden', String(!open));
      document.body.style.overflow = open ? 'hidden' : '';
    });
    $$('a', mm).forEach(a => a.addEventListener('click', closeMenu));
  }

  // === Reveal from left / right / below ===
  const io = new IntersectionObserver(es => es.forEach(e => {
    if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
  }), { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
  $$('[data-reveal]').forEach(el => {
    const sib = el.parentElement ? [...el.parentElement.children].filter(c => c.hasAttribute('data-reveal')) : [];
    el.style.setProperty('--d', Math.min(sib.indexOf(el), 6) * 0.08 + 's');
    io.observe(el);
  });

  // === Count-up numbers ===
  const cio = new IntersectionObserver(es => es.forEach(e => {
    if (!e.isIntersecting) return;
    const el = e.target, to = +el.dataset.count, t0 = performance.now(), dur = reduce ? 0 : 1200;
    const tick = now => {
      const t = dur ? Math.min(1, (now - t0) / dur) : 1;
      el.textContent = Math.round(to * (1 - Math.pow(1 - t, 3)));
      if (t < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
    cio.unobserve(el);
  }), { threshold: 0.6 });
  $$('[data-count]').forEach(el => cio.observe(el));

  // === Scroll-linked: nav, sticky bar, parallax shapes, line drawing ===
  const sticky = $('#stickyOrder'), hero = $('#hero'), navEl = $('#nav');
  const blobs = $$('[data-speed]'), draws = $$('.draw');
  draws.forEach(p => { try { p.setAttribute('pathLength', '1'); } catch (e) {} });
  let ticking = false, lastY = scrollY, idle = 0;
  // order bar (phones): shows only while the visitor scrolls UP, hides when scrolling down or stopping
  const hideBar = () => sticky && sticky.classList.remove('is-visible');
  const onScroll = () => {
    ticking = false;
    const y = scrollY, vh = innerHeight, dy = y - lastY;
    if (navEl) navEl.classList.toggle('is-scrolled', y > 24);
    lastY = y;
    if (sticky && Math.abs(dy) > 3) {
      const pastHero = hero ? y > hero.offsetHeight * 0.7 : y > 200;
      sticky.classList.toggle('is-visible', dy < 0 && pastHero);
      clearTimeout(idle);
      if (dy < 0) idle = setTimeout(hideBar, 1400);
    }
    if (reduce) return;
    blobs.forEach(b => {
      const r = b.parentElement.getBoundingClientRect();
      b.style.transform = `translate3d(0, ${((r.top + r.height / 2) - vh / 2) * +b.dataset.speed}px, 0)`;
    });
    draws.forEach(p => {
      const r = p.ownerSVGElement.getBoundingClientRect();
      const t = Math.min(1, Math.max(0, (vh - r.top) / (vh * 0.7)));
      p.style.setProperty('--p', t.toFixed(3));
    });
  };
  window.addEventListener('scroll', () => { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  onScroll();

  // === Review rows: drift continuously, speed up with scroll velocity ===
  const rows = $$('.mq-track');
  if (rows.length) {
    const st = rows.map((t, i) => ({ t, x: 0, dir: i % 2 ? 1 : -1, w: 0 }));
    const measureRows = () => st.forEach(r => { r.w = r.t.scrollWidth / 2; if (r.dir > 0 && !r.x) r.x = -r.w; });
    measureRows(); window.addEventListener('resize', measureRows);
    let lastY = scrollY, boost = 0, prev = 0, visible = false, paused = false;
    new IntersectionObserver(es => { visible = es[0].isIntersecting; if (visible) requestAnimationFrame(frame); }).observe(rows[0].closest('.mq'));
    rows[0].closest('.mq').addEventListener('mouseenter', () => { paused = true; });
    rows[0].closest('.mq').addEventListener('mouseleave', () => { paused = false; });
    window.addEventListener('scroll', () => { boost = Math.min(18, boost + Math.abs(scrollY - lastY) * 0.06); lastY = scrollY; }, { passive: true });
    function frame(now) {
      const dt = prev ? Math.min(0.05, (now - prev) / 1000) : 0.016; prev = now;
      boost *= Math.pow(0.04, dt);                         // decays in about a second
      const v = reduce ? 0 : (paused ? 0 : 38 + boost * 60);
      st.forEach((r, i) => {
        r.x += r.dir * v * (1 + i * 0.12) * dt;
        if (r.x <= -r.w) r.x += r.w;
        if (r.x > 0) r.x -= r.w;
        let x = r.x + r.dir * scrollY * 0.45; x = ((x % r.w) + r.w) % r.w - r.w;
        r.t.style.transform = `translate3d(${x.toFixed(1)}px,0,0)`;
      });
      if (visible) requestAnimationFrame(frame); else prev = 0;
    }
  }

  // === "Back" links: return to the exact page the visitor came from on this site ===
  $$('[data-back]').forEach(a => a.addEventListener('click', e => {
    try {
      if (document.referrer && new URL(document.referrer).origin === location.origin && history.length > 1) { e.preventDefault(); history.back(); }
    } catch (err) {}
  }));

  // === Speed: keep the site in a local cache (sw.js) and prefetch pages before the click ===
  if ('serviceWorker' in navigator && location.protocol === 'https:') {
    addEventListener('load', () => navigator.serviceWorker.register('/sw.js').catch(() => {}));
  }
  if (HTMLScriptElement.supports && HTMLScriptElement.supports('speculationrules')) {
    const sr = document.createElement('script');
    sr.type = 'speculationrules';
    sr.textContent = JSON.stringify({ prefetch: [{ source: 'document', where: { and: [{ href_matches: '/*' }, { not: { href_matches: '/(api|admin)/*' } }] }, eagerness: 'moderate' }] });
    document.head.appendChild(sr);
  }

  // === Map: Google Maps loads only when the visitor asks for it (no Google cookies before that) ===
  $$('.map-load').forEach(b => b.addEventListener('click', () => {
    const f = document.createElement('iframe');
    f.src = b.dataset.src; f.title = "Kiwi's на картата — ул. Никола Карев 14, Пловдив";
    f.width = '100%'; f.height = '100%'; f.style.border = '0'; f.loading = 'lazy'; f.referrerPolicy = 'no-referrer-when-downgrade'; f.allowFullscreen = true;
    b.replaceWith(f);
  }));

  // === Reviews: show all ===
  const more = $('#rvMore'), grid = $('#rvGrid');
  if (more && grid) more.addEventListener('click', () => { grid.hidden = false; grid.classList.add('is-all'); more.remove(); grid.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' }); });

  // === Gallery lightbox ===
  const lb = $('#lb');
  if (lb) {
    const items = $$('.g'), img = $('#lbImg'), cap = $('#lbCap');
    let n = 0, last = null;
    const open = k => {
      n = (k + items.length) % items.length;
      img.src = items[n].dataset.full;
      img.alt = items[n].getAttribute('aria-label') || '';
      cap.textContent = '';
      lb.hidden = false; document.body.style.overflow = 'hidden';
    };
    const close = () => { lb.hidden = true; document.body.style.overflow = ''; if (last) last.focus(); };
    items.forEach((it, k) => it.addEventListener('click', () => { last = it; open(k); $('#lbX').focus(); }));
    $('#lbX').addEventListener('click', close);
    $('#lbPrev').addEventListener('click', () => open(n - 1));
    $('#lbNext').addEventListener('click', () => open(n + 1));
    lb.addEventListener('click', e => { if (e.target === lb) close(); });
    document.addEventListener('keydown', e => {
      if (lb.hidden) return;
      if (e.key === 'Escape') close();
      if (e.key === 'ArrowLeft') open(n - 1);
      if (e.key === 'ArrowRight') open(n + 1);
    });
    let x0 = null;
    lb.addEventListener('touchstart', e => { x0 = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener('touchend', e => {
      if (x0 === null) return;
      const dx = e.changedTouches[0].clientX - x0; x0 = null;
      if (Math.abs(dx) > 40) open(n + (dx < 0 ? 1 : -1));
    });
  }
});
