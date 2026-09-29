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

  // === Mobile menu ===
  const hamburger = document.getElementById('hamburger');
  const mobileMenu = document.getElementById('mobileMenu');
  const mmClose = document.getElementById('mmClose');

  function closeMobileMenu() {
    mobileMenu.classList.remove('is-open');
    hamburger.classList.remove('is-active');
    document.body.style.overflow = '';
  }

  hamburger.addEventListener('click', () => {
    const open = mobileMenu.classList.toggle('is-open');
    hamburger.classList.toggle('is-active');
    document.body.style.overflow = open ? 'hidden' : '';
  });

  mmClose.addEventListener('click', closeMobileMenu);

  mobileMenu.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', closeMobileMenu);
  });

  // === Nav scroll ===
  const nav = document.getElementById('nav');
  window.addEventListener('scroll', () => {
    nav.classList.toggle('is-scrolled', scrollY > 30);
  }, { passive: true });

  // === Reveal on scroll ===
  const sectionObs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        e.target.style.opacity = '1';
        e.target.style.transform = 'none';
        sectionObs.unobserve(e.target);
      }
    });
  }, { threshold: 0.08 });

  document.querySelectorAll('.cat-card, .about-grid, .visit-card, .about-img').forEach((el, i) => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(20px)';
    el.style.transition = `opacity 0.6s ${0.05 * i}s cubic-bezier(0.22,1,0.36,1), transform 0.6s ${0.05 * i}s cubic-bezier(0.22,1,0.36,1)`;
    sectionObs.observe(el);
  });

  // === Smooth scroll ===
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
      const id = a.getAttribute('href');
      if (id === '#') return;
      const t = document.querySelector(id);
      if (t) { e.preventDefault(); t.scrollIntoView({ behavior: 'smooth' }); }
    });
  });
});
