"""js/join.js — the "join the Kiwi's family" card. The kiwi bird is the same drawing as in the
intro (paths taken from js/preloader.js), animated with CSS: it hops, pecks at a kiwi slice and the
slice bounces. usage: python3 -I scripts/gen/build_join.py js/preloader.js js/join.js"""
import re, sys

src, out = sys.argv[1], sys.argv[2]
pre = open(src, encoding="utf-8").read()
P = {k: re.search(rf"{k}: new Path2D\('([^']+)'\)", pre).group(1) for k in ("body", "head", "backLeg", "frontLeg")}

svg = (
    '<svg class="kj-bird" viewBox="-24 -46 64 52" aria-hidden="true">'
    '<ellipse class="kj-shadow" cx="2" cy="1.2" rx="17" ry="1.6"/>'
    '<g class="kj-hop">'
    f'<path class="kj-leg kj-leg--b" d="{P["backLeg"]}"/>'
    f'<path class="kj-leg kj-leg--f" d="{P["frontLeg"]}"/>'
    f'<path d="{P["body"]}" fill-rule="evenodd"/>'
    f'<g class="kj-head"><path d="{P["head"]}" fill-rule="evenodd"/></g>'
    '</g>'
    '<g class="kj-fruit"><ellipse cx="33" cy="-2.6" rx="3.4" ry="2.6" fill="#7FAF3A"/>'
    '<ellipse cx="33" cy="-2.6" rx="2.5" ry="1.8" fill="#A8D462"/><ellipse cx="33" cy="-2.6" rx=".8" ry=".55" fill="#FAF6F0"/></g>'
    '</svg>'
)

js = r"""/* "Join the Kiwi's family" — newsletter card (double opt-in, see /api/subscribe.php).
   Appears 5 s after the page opens; "Не сега" hides it for 14 days, signing up hides it for good. */
(function () {
  'use strict';
  var KEY = 'kiwi-join', SHOW_AFTER = 5000, SNOOZE = 14 * 864e5;
  var get = function () { try { return JSON.parse(localStorage.getItem(KEY) || 'null'); } catch (e) { return null; } };
  var set = function (v) { try { localStorage.setItem(KEY, JSON.stringify(v)); } catch (e) {} };
  var en = function () { return document.documentElement.getAttribute('data-lang') === 'en'; };
  var T = {
    bg: { kicker: 'Семейството на Kiwi\'s', title: 'Стани част от семейството', text: 'Нови ястия, промоции и покани — първо при теб, директно в пощата.',
          first: 'Име', last: 'Фамилия', email: 'Имейл', consent: 'Съгласен/на съм Kiwi\'s да ми изпраща имейли с новини и промоции. Мога да се отпиша по всяко време.',
          privacy: 'Поверителност', go: 'Присъедини се', later: 'Не сега', close: 'Затвори',
          ok: 'Почти готово! Изпратихме ти имейл — натисни линка в него, за да потвърдиш.', err: 'Нещо се обърка. Опитай пак след малко.',
          rate: 'Твърде много опити. Опитай пак по-късно.', bad: 'Провери полетата.', welcome: 'Добре дошъл/дошла в семейството на Kiwi\'s!',
          expired: 'Линкът за потвърждение е изтекъл. Запиши се отново.' },
    en: { kicker: 'The Kiwi\'s family', title: 'Join the family', text: 'New dishes, offers and invitations — first to you, straight to your inbox.',
          first: 'First name', last: 'Last name', email: 'Email', consent: 'I agree that Kiwi\'s may email me news and offers. I can unsubscribe at any time.',
          privacy: 'Privacy', go: 'Join', later: 'Not now', close: 'Close',
          ok: 'Almost there! We sent you an email — click the link in it to confirm.', err: 'Something went wrong. Please try again.',
          rate: 'Too many attempts. Please try later.', bad: 'Please check the fields.', welcome: 'Welcome to the Kiwi\'s family!',
          expired: 'The confirmation link has expired. Please sign up again.' }
  };
  var t = function (k) { return T[en() ? 'en' : 'bg'][k]; };
  var BIRD = '__SVG__';

  function toast(text) {
    var d = document.createElement('div');
    d.className = 'kj-toast'; d.setAttribute('role', 'status');
    d.innerHTML = BIRD + '<p></p>'; d.querySelector('p').textContent = text;
    document.body.appendChild(d);
    requestAnimationFrame(function () { d.classList.add('in'); });
    setTimeout(function () { d.classList.remove('in'); setTimeout(function () { d.remove(); }, 600); }, 6000);
  }

  function build() {
    var el = document.createElement('aside');
    el.className = 'kj'; el.setAttribute('aria-labelledby', 'kjTitle');
    el.innerHTML =
      '<button class="kj-x" type="button" aria-label="' + t('close') + '">&times;</button>' +
      '<div class="kj-top">' + BIRD + '<div><span class="kj-kicker">' + t('kicker') + '</span><h2 id="kjTitle">' + t('title') + '</h2></div></div>' +
      '<p class="kj-text">' + t('text') + '</p>' +
      '<form class="kj-form" novalidate>' +
        '<div class="kj-row"><label><span>' + t('first') + '</span><input name="first" autocomplete="given-name" maxlength="60" required></label>' +
        '<label><span>' + t('last') + '</span><input name="last" autocomplete="family-name" maxlength="60" required></label></div>' +
        '<label><span>' + t('email') + '</span><input name="email" type="email" autocomplete="email" maxlength="160" required></label>' +
        '<label class="kj-hp" aria-hidden="true">Website<input name="website" tabindex="-1" autocomplete="off"></label>' +
        '<label class="kj-check"><input type="checkbox" name="consent" required><span>' + t('consent') + ' <a href="/privacy.php">' + t('privacy') + '</a></span></label>' +
        '<p class="kj-msg" role="status" aria-live="polite"></p>' +
        '<div class="kj-btns"><button class="kj-go" type="submit">' + t('go') + '</button><button class="kj-later" type="button">' + t('later') + '</button></div>' +
      '</form>';
    document.body.appendChild(el);
    var opened = Date.now();
    var form = el.querySelector('form'), msg = el.querySelector('.kj-msg'), go = el.querySelector('.kj-go');
    var close = function (snooze) {
      el.classList.remove('in');
      if (snooze) set({ s: 'later', at: Date.now() });
      setTimeout(function () { el.remove(); }, 600);
    };
    el.querySelector('.kj-x').addEventListener('click', function () { close(true); });
    el.querySelector('.kj-later').addEventListener('click', function () { close(true); });
    document.addEventListener('keydown', function esc(e) { if (e.key === 'Escape' && document.body.contains(el)) { close(true); document.removeEventListener('keydown', esc); } });
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var f = form.elements, bad = false;
      ['first', 'last', 'email'].forEach(function (n) {
        var ok = f[n].value.trim() !== '' && (n !== 'email' || /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(f[n].value.trim()));
        f[n].closest('label').classList.toggle('bad', !ok); if (!ok) bad = true;
      });
      f.consent.closest('label').classList.toggle('bad', !f.consent.checked); if (!f.consent.checked) bad = true;
      if (bad) { msg.textContent = t('bad'); return; }
      go.disabled = true; msg.textContent = '';
      fetch('/api/subscribe.php', { method: 'POST', headers: { 'Content-Type': 'application/json' }, credentials: 'same-origin',
        body: JSON.stringify({ first: f.first.value, last: f.last.value, email: f.email.value, consent: f.consent.checked, website: f.website.value, t: Date.now() - opened }) })
        .then(function (r) { return r.json().then(function (j) { return { s: r.status, j: j }; }); })
        .then(function (r) {
          if (r.j && r.j.ok) {
            set({ s: 'done', at: Date.now() });
            el.classList.add('is-done');
            form.innerHTML = '<p class="kj-done">' + t('ok') + '</p>';
            setTimeout(function () { close(false); }, 7000);
          } else { msg.textContent = r.s === 429 ? t('rate') : r.s === 422 ? t('bad') : t('err'); go.disabled = false; }
        })
        .catch(function () { msg.textContent = t('err'); go.disabled = false; });
    });
    requestAnimationFrame(function () { requestAnimationFrame(function () { el.classList.add('in'); }); });
  }

  document.addEventListener('DOMContentLoaded', function () {
    var q = new URLSearchParams(location.search), joined = q.get('joined');
    if (joined) {
      history.replaceState(null, '', location.pathname + location.hash);
      if (joined === 'ok') { set({ s: 'done', at: Date.now() }); toast(t('welcome')); return; }
      toast(t('expired'));
    }
    var st = get();
    if (st && (st.s === 'done' || (st.s === 'later' && Date.now() - st.at < SNOOZE))) return;
    setTimeout(build, SHOW_AFTER);
  });
})();
"""
open(out, "w", encoding="utf-8").write(js.replace("'__SVG__'", "'" + svg.replace("'", "\\'") + "'"))
print("join ok", len(svg))
