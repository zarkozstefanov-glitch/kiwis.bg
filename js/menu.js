document.addEventListener('DOMContentLoaded', () => {

  // === Language Toggle ===
  function setLang(lang) {
    document.documentElement.setAttribute('data-lang', lang);
    document.documentElement.setAttribute('lang', lang);
    localStorage.setItem('kiwi-lang', lang);
    document.querySelectorAll('[data-en]').forEach(el => {
      if (!el.dataset.bg) el.dataset.bg = el.innerHTML;
      el.innerHTML = lang === 'en' ? el.dataset.en : el.dataset.bg;
    });
    document.querySelectorAll('.lang-btn').forEach(b => {
      b.classList.toggle('is-active', b.dataset.lang === lang);
    });
  }

  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.addEventListener('click', () => setLang(btn.dataset.lang));
  });

  const savedLang = localStorage.getItem('kiwi-lang');
  if (savedLang && savedLang !== 'bg') setLang(savedLang);

  // === Pills / Category Navigation ===
  const pills = document.querySelectorAll('.pill');
  const sections = document.querySelectorAll('.cat');
  const pillsBar = document.getElementById('pills');

  pills.forEach(pill => {
    pill.addEventListener('click', () => {
      const cat = pill.dataset.cat;

      pills.forEach(p => p.classList.remove('is-active'));
      pill.classList.add('is-active');

      const target = document.querySelector(`.cat[data-category="${cat}"]`);
      if (target) {
        const offset = pillsBar.getBoundingClientRect().bottom;
        const top = target.getBoundingClientRect().top + window.scrollY - offset - 8;
        window.scrollTo({ top, behavior: 'smooth' });
      }

      pill.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
    });
  });

  // === Highlight active pill on scroll ===
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const cat = entry.target.dataset.category;
        pills.forEach(p => {
          p.classList.toggle('is-active', p.dataset.cat === cat);
        });
        const activePill = document.querySelector(`.pill[data-cat="${cat}"]`);
        if (activePill) {
          activePill.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
        }
      }
    });
  }, {
    rootMargin: '-120px 0px -60% 0px',
    threshold: 0
  });

  sections.forEach(s => observer.observe(s));
});
