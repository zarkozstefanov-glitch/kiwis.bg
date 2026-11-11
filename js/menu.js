document.addEventListener('DOMContentLoaded', () => {
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
  }
  $$('.lang-btn').forEach(btn => btn.addEventListener('click', () => setLang(btn.dataset.lang)));
  let saved = null;
  try { saved = localStorage.getItem('kiwi-lang'); } catch (e) {}
  if (saved && saved !== 'bg') setLang(saved);

  // === Category pills: jump + follow the scroll ===
  const pills = $$('.pill');
  const bar = document.getElementById('pills');
  pills.forEach(pill => pill.addEventListener('click', () => {
    const t = document.getElementById(pill.dataset.cat);
    if (!t) return;
    const top = t.getBoundingClientRect().top + scrollY - bar.getBoundingClientRect().bottom + 8;
    window.scrollTo({ top, behavior: reduce ? 'auto' : 'smooth' });
  }));
  const setActive = id => {
    pills.forEach(p => p.classList.toggle('is-active', p.dataset.cat === id));
    const a = pills.find(p => p.dataset.cat === id);
    if (a) bar.scrollTo({ left: a.offsetLeft - bar.clientWidth / 2 + a.clientWidth / 2, behavior: reduce ? 'auto' : 'smooth' });
  };
  const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) setActive(e.target.id); }), { rootMargin: '-140px 0px -55% 0px' });
  $$('.cat').forEach(s => io.observe(s));
});
