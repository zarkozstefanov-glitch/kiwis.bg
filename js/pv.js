/* Product viewer on a green podium.
   - default: one product on the podium, the next arrives from behind on a curve
   - data-loop: endless carousel; neighbours stay visible on both sides
   - data-scroll: on wide screens the page scroll turns the podium (pinned section);
     with data-loop the scroll runs one full turn, back to the first dish, and the
     arrows keep turning past the ends */
(function () {
  'use strict';
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var wide = window.matchMedia('(min-width: 960px) and (min-height: 600px)');
  var mod = function (a, n) { return ((a % n) + n) % n; };

  function init(root) {
    var items = [].slice.call(root.querySelectorAll('.pv-item'));
    var panels = [].slice.call(root.querySelectorAll('.pv-panel'));
    var thumbs = [].slice.call(root.querySelectorAll('.pv-th'));
    var dots = [].slice.call(root.querySelectorAll('.pv-dots i'));
    var stage = root.querySelector('.pv-stage');
    var turn = root.querySelector('.pv-turn');
    var turnN = root.querySelector('.pv-turn-n');
    var n = items.length;
    if (!n) return;
    var loop = root.hasAttribute('data-loop') && n > 2;
    var wrap = root.closest('.pv-scroll');
    var cur = 0, target = 0, active = -1, W = 400, H = 400;
    var shrink = root.querySelector('.pv-item--flat') ? 2.7 : 1.7;   // wide plates: smaller neighbours so they never overlap

    function measure() { W = stage.clientWidth; H = stage.clientHeight; }

    function render(p) {
      for (var i = 0; i < n; i++) {
        var d = i - p;
        if (loop) d = d - n * Math.round(d / n);             // shortest way round
        var ad = Math.abs(d), it = items[i];
        var limit = loop ? 1.7 : 1.25;
        if (ad > limit) { it.style.visibility = 'hidden'; it.style.opacity = '0'; continue; }
        var a, x, y, s, op, blur;
        if (loop) {                                          // neighbours visible left & right
          a = d * (Math.PI / 4.4);
          x = Math.sin(a) * W * 0.5;
          y = -(1 - Math.cos(a)) * H * 0.36;
          s = Math.max(0.2, 1 - (1 - Math.cos(a)) * shrink);
          op = ad < 1.05 ? 1 - ad * 0.38 : Math.max(0, 0.62 - (ad - 1.05) * 0.95);
          blur = ad * 1.6;
        } else {
          a = d * (Math.PI / 2.3);
          x = Math.sin(a) * W * 0.4;
          y = -(1 - Math.cos(a)) * H * 0.3;
          s = 1 - (1 - Math.cos(a)) * 0.62;
          op = Math.max(0, 1 - Math.pow(ad, 1.6) * 0.9);
          blur = ad * 6;
        }
        it.style.visibility = 'visible';
        it.style.opacity = op.toFixed(3);
        it.style.transform = 'translate3d(calc(-50% + ' + x.toFixed(1) + 'px),' + y.toFixed(1) + 'px,0) scale(' + s.toFixed(3) + ')';
        it.style.filter = ad > 0.04 ? 'blur(' + blur.toFixed(1) + 'px) brightness(' + (1 - Math.min(ad, 1) * 0.25).toFixed(2) + ')' : 'none';
        it.style.zIndex = String(100 - Math.round(ad * 40));
        it.classList.toggle('is-front', ad < 0.5);
      }
      root.style.setProperty('--rot', (p * 48).toFixed(1) + 'deg');
      var k = loop ? mod(Math.round(p), n) : Math.max(0, Math.min(n - 1, Math.round(p)));
      if (k !== active) setActive(k);
    }

    function updateTurn() {
      if (!turn) return;
      var img = items[active].querySelector('.pv-img');
      var has = !!(img && img.dataset.alt);
      turn.hidden = !has;
      if (has && turnN) turnN.textContent = (img.dataset.shot || '1') + '/2';
    }

    function setActive(k) {
      active = k;
      panels.forEach(function (pn, i) { var on = i === k; pn.classList.toggle('is-on', on); if (on) pn.removeAttribute('aria-hidden'); else pn.setAttribute('aria-hidden', 'true'); });
      thumbs.forEach(function (t, i) { var on = i === k; t.classList.toggle('is-on', on); t.setAttribute('aria-selected', String(on)); });
      dots.forEach(function (d, i) { d.classList.toggle('on', i === k); });
      updateTurn();
      var th = thumbs[k], bar = th && th.parentElement;
      if (bar && bar.scrollWidth > bar.clientWidth) {
        bar.scrollTo({ left: th.offsetLeft - bar.clientWidth / 2 + th.clientWidth / 2, behavior: reduce ? 'auto' : 'smooth' });
      }
    }

    var running = false, last = 0;
    function loopFrame(now) {
      var dt = last ? Math.min(0.05, (now - last) / 1000) : 0.016; last = now;
      cur += (target - cur) * (reduce ? 1 : Math.min(1, dt * 7));
      if (Math.abs(target - cur) < 0.001) cur = target;
      render(cur);
      if (cur !== target) requestAnimationFrame(loopFrame); else { running = false; last = 0; }
    }
    function kick() { if (!running) { running = true; requestAnimationFrame(loopFrame); } }

    var pinned = false;
    function setMode() {
      pinned = !!wrap && wide.matches;
      if (wrap) wrap.classList.toggle('is-pinned', pinned);
      measure(); render(cur);
    }
    var offset = 0;                                        // arrow/thumb steps taken while pinned
    function scrollPos() {
      var r = wrap.getBoundingClientRect(), total = wrap.offsetHeight - window.innerHeight;
      var t = total > 0 ? Math.min(1, Math.max(0, -r.top / total)) : 0;
      // data-steps: how many dishes the page scroll turns through before the page moves on (arrows keep going)
      var steps = wrap.hasAttribute('data-steps') ? Math.min(+wrap.dataset.steps, loop ? n : n - 1) : (loop ? n : n - 1);
      var raw = t * steps, k = Math.floor(raw), f = raw - k;
      var g = Math.min(1, Math.max(0, (f - 0.35) / 0.3));
      return Math.min(steps, k + g * g * (3 - 2 * g));
    }
    function fromScroll() {
      if (!pinned) return;
      target = scrollPos() + offset;
      kick();
    }
    function step(dir) { go(loop ? Math.round(target) + dir : active + dir, true); }
    function go(k, relative) {
      if (loop) {
        if (!relative) {                                   // jump to item k the short way round
          var base = Math.round(target), dd = mod(k - mod(base, n), n);
          if (dd > n / 2) dd -= n;
          k = base + dd;
        }
        if (pinned) offset += k - target;                  // page stays where it is, only the podium turns
        target = k;
      } else if (pinned) {
        k = Math.max(0, Math.min(n - 1, k));
        var total = wrap.offsetHeight - window.innerHeight;
        window.scrollTo({ top: wrap.getBoundingClientRect().top + window.scrollY + total * (k / Math.max(1, n - 1)), behavior: reduce ? 'auto' : 'smooth' });
        return;
      } else target = Math.max(0, Math.min(n - 1, k));
      kick();
    }

    root.querySelector('.pv-prev').addEventListener('click', function () { step(-1); });
    root.querySelector('.pv-next').addEventListener('click', function () { step(1); });
    thumbs.forEach(function (t, i) { t.addEventListener('click', function () { go(i); }); });
    items.forEach(function (it, i) { it.addEventListener('click', function () { if (i !== active) go(i); else if (turn && !turn.hidden) turn.click(); }); });
    root.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight') { e.preventDefault(); step(1); }
      if (e.key === 'ArrowLeft') { e.preventDefault(); step(-1); }
    });
    var x0 = null, y0 = null;
    stage.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; y0 = e.touches[0].clientY; }, { passive: true });
    stage.addEventListener('touchend', function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0, dy = e.changedTouches[0].clientY - y0; x0 = null;
      if (Math.abs(dx) > 40 && Math.abs(dx) > Math.abs(dy)) step(dx < 0 ? 1 : -1);
    });
    if (turn) turn.addEventListener('click', function () {
      var img = items[active].querySelector('.pv-img'), refl = items[active].querySelector('.pv-refl');
      if (!img || !img.dataset.alt) return;
      var a = img.dataset.alt; img.dataset.alt = img.currentSrc || img.src;
      img.dataset.shot = img.dataset.shot === '2' ? '1' : '2';
      img.removeAttribute('srcset'); img.classList.remove('spin'); void img.offsetWidth; img.classList.add('spin');
      img.src = a; if (refl) refl.src = a.replace('-900.webp', '-500.webp');
      updateTurn();
    });

    window.addEventListener('scroll', fromScroll, { passive: true });
    window.addEventListener('resize', function () { setMode(); fromScroll(); });
    if (wide.addEventListener) wide.addEventListener('change', setMode);
    setMode(); fromScroll(); render(cur);

    new IntersectionObserver(function (es, o) {
      if (es[0].isIntersecting) { root.classList.add('in'); o.disconnect(); }
    }, { threshold: 0.2 }).observe(root);
  }

  document.addEventListener('DOMContentLoaded', function () {
    [].forEach.call(document.querySelectorAll('[data-pv]'), init);
  });
})();
