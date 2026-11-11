<?php
declare(strict_types=1);
require __DIR__ . '/api/_lib.php';
header('Content-Type: text/html; charset=utf-8');
$h = fn($s) => htmlspecialchars((string)$s, ENT_QUOTES);
try { $co = k_setting('company', ''); $eik = k_setting('eik', ''); $adr = k_setting('company_address', ''); $mail = k_setting('contact_email', ''); }
catch (Throwable $e) { $co = $eik = $adr = $mail = ''; }
$who = $co !== '' ? $h($co) . ($eik !== '' ? ', ЕИК ' . $h($eik) : '') . ($adr !== '' ? ', ' . $h($adr) : '') : "Kiwi's, ул. „Никола Карев“ 14, Пловдив";
$contact = ($mail !== '' ? '<a href="mailto:' . $h($mail) . '">' . $h($mail) . '</a> или ' : '') . '<a href="tel:+359892632470">+359 892 632 470</a>';
?>
<!DOCTYPE html>
<html lang="bg" data-lang="bg">
<head>
  <meta charset="UTF-8">
  <style>@view-transition{navigation:auto}</style>
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <title>Поверителност — Kiwi's</title>
  <meta name="robots" content="noindex, follow">
  <link rel="icon" href="/favicon.ico" sizes="48x48">
  <link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..900;1,9..144,300..900&family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/css/style.css">
  <link rel="stylesheet" href="/css/blog.css">
</head>
<body class="blog">
  <a class="skip" href="#main" data-en="Skip to content">Към съдържанието</a>
  <header class="nav" id="nav">
    <div class="nav-bar">
      <a href="/" class="nav-logo" aria-label="Kiwi's — начало"><img src="/images/kiwi-icon.jpg" alt="" width="38" height="38"><span class="nav-brand">KiWi'S</span></a>
      <nav class="nav-links" aria-label="Основна навигация"><a href="/#about" data-en="About">За нас</a><a href="/#reviews" data-en="Reviews">Отзиви</a><a href="/blog/" data-en="Articles" >Статии</a><a href="/#visit" data-en="Contact">Контакти</a><a href="/menu.html" data-en="Menu">Меню</a></nav>
      <div class="nav-right">
        <div class="lang-toggle"><button class="lang-btn is-active" data-lang="bg" aria-label="Български">BG</button><button class="lang-btn" data-lang="en" aria-label="English">EN</button></div>
        <a href="https://glovoapp.com/bg/bg/plovdiv/stores/kiwis-pdv" class="nav-cta" target="_blank" rel="noopener"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 17h-2v-6l2-5h9l4 5h1a2 2 0 012 2v4h-2"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/><path d="M9 17h6"/></svg><span data-en="Order">Поръчай</span></a>
        <button class="hamburger" id="hamburger" aria-label="Меню" aria-expanded="false"><span></span><span></span></button>
      </div>
    </div>
  </header>
  <div class="mobile-menu" id="mobileMenu" aria-hidden="true">
    <div class="mm-inner">
      <a href="/#about" class="mm-link" data-en="About">За нас</a><a href="/#reviews" class="mm-link" data-en="Reviews">Отзиви</a><a href="/blog/" class="mm-link" data-en="Articles">Статии</a><a href="/#visit" class="mm-link" data-en="Contact">Контакти</a><a href="/menu.html" class="mm-link" data-en="Menu">Меню</a>
      <a href="https://glovoapp.com/bg/bg/plovdiv/stores/kiwis-pdv" class="btn btn--glovo btn--lg mm-cta" target="_blank" rel="noopener"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 17h-2v-6l2-5h9l4 5h1a2 2 0 012 2v4h-2"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/><path d="M9 17h6"/></svg><span data-en="Order on Glovo">Поръчай в Glovo</span></a>
      <p class="mm-info"><span data-en="Mon — Sat, 09:00 — 21:30">Пон — Съб, 09:00 — 21:30</span><br><a href="tel:+359892632470">+359 892 632 470</a></p>
      <a href="https://www.instagram.com/kiwis.bg/" class="mm-ig" target="_blank" rel="noopener"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2.5" y="2.5" width="19" height="19" rx="5.5"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.6" cy="6.4" r="1.1" fill="currentColor" stroke="none"/></svg><span>@kiwis.bg</span></a>
    </div>
  </div>

  <main id="main">
    <article class="post">
      <div class="container post-head">
        <a class="back-link" href="/" data-back aria-label="Назад"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M15 18l-6-6 6-6"/></svg><span>Назад</span></a>
        <h1>Поверителност</h1>
        <p class="post-meta">Как пазим името и имейла ти, когато се запишеш за новини от Kiwi's.</p>
      </div>
      <div class="container post-body">
<h2>Кой обработва данните</h2>
<p><?= $who ?>. За въпроси: <?= $contact ?>.</p>
<h2>Какви данни събираме</h2>
<p>Само когато сам/а се запишеш: име, фамилия и имейл, датата и текста на съгласието ти. Не събираме данни за посещенията ти и сайтът не използва бисквитки за реклама или проследяване.</p>
<h2>За какво ги използваме</h2>
<p>За да ти пращаме имейли с новини, нови ястия и промоции от Kiwi's. Основание: твоето съгласие (чл. 6, ал. 1, буква „а“ от Регламент (ЕС) 2016/679). Записването става в две стъпки — след формата ти изпращаме линк за потвърждение. Ако не го потвърдиш до 48 часа, данните се изтриват автоматично.</p>
<h2>Как ги пазим</h2>
<p>Данните се съхраняват криптирани на нашия сървър в България и не се дават на трети лица. Достъп до тях има само Kiwi's.</p>
<h2>Колко време</h2>
<p>Докато не се отпишеш. Всеки имейл от нас има линк „Отпиши се“ — с него името и имейлът ти се изтриват веднага.</p>
<h2>Твоите права</h2>
<p>Можеш по всяко време да оттеглиш съгласието си, да поискаш достъп до данните си, поправка или изтриване, като ни пишеш или се обадиш. Имаш право и на жалба до Комисията за защита на личните данни (<a href="https://www.cpdp.bg" target="_blank" rel="noopener">cpdp.bg</a>).</p>
      </div>
    </article>
  </main>
  <footer class="footer">
    <div class="container footer-inner">
      <div class="footer-brand"><img src="/images/kiwi-icon.jpg" alt="" width="40" height="40"><div><strong>KiWi'S</strong><span data-en="14 Nikola Karev St., Plovdiv · Mon–Sat 09:00–21:30">ул. „Никола Карев“ 14, Пловдив · Пон–Съб 09:00–21:30</span></div></div>
      <nav class="footer-links" aria-label="Footer">
        <a href="/menu.html" data-en="Menu">Меню</a><a href="/blog/" data-en="Articles">Статии</a>
        <a href="https://glovoapp.com/bg/bg/plovdiv/stores/kiwis-pdv" target="_blank" rel="noopener">Glovo</a>
        <a href="https://www.google.com/maps?cid=1892105797985093642" target="_blank" rel="noopener" data-en="Google reviews">Отзиви в Google</a>
        <a href="https://www.instagram.com/kiwis.bg/" target="_blank" rel="noopener" class="ft-ig"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2.5" y="2.5" width="19" height="19" rx="5.5"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.6" cy="6.4" r="1.1" fill="currentColor" stroke="none"/></svg><span>Instagram</span></a>
        <a href="tel:+359892632470">+359 892 632 470</a>
        <a href="/privacy.php" data-en="Privacy">Поверителност</a>
      </nav>
      <p class="footer-copy">&copy; 2026 KiWi'S</p>
    </div>
  </footer>

  <script src="/js/main.js"></script>
</body>
</html>
