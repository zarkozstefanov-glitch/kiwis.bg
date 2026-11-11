"""privacy.php — privacy notice for the newsletter (GDPR art. 13). Company details come from the
admin settings at request time. usage: python3 -I scripts/gen/build_privacy.py scripts/gen privacy.php"""
import sys
S, OUT = sys.argv[1], sys.argv[2]
sys.path.insert(0, S)
from pv_lib import nav, footer

FONT = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300..900;1,9..144,300..900&family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">'

php = '''<?php
declare(strict_types=1);
require __DIR__ . '/api/_lib.php';
header('Content-Type: text/html; charset=utf-8');
$h = fn($s) => htmlspecialchars((string)$s, ENT_QUOTES);
try { $co = k_setting('company', ''); $eik = k_setting('eik', ''); $adr = k_setting('company_address', ''); $mail = k_setting('contact_email', ''); }
catch (Throwable $e) { $co = $eik = $adr = $mail = ''; }
$who = $co !== '' ? $h($co) . ($eik !== '' ? ', ЕИК ' . $h($eik) : '') . ($adr !== '' ? ', ' . $h($adr) : '') : "Kiwi's, ул. „Никола Карев“ 14, Пловдив";
$contact = ($mail !== '' ? '<a href="mailto:' . $h($mail) . '">' . $h($mail) . '</a> или ' : '') . '<a href="tel:+359892632470">+359 892 632 470</a>';
?>'''

body = f'''<!DOCTYPE html>
<html lang="bg" data-lang="bg">
<head>
  <meta charset="UTF-8">
  <style>@view-transition{{navigation:auto}}</style>
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <title>Поверителност — Kiwi's</title>
  <meta name="robots" content="noindex, follow">
  <link rel="icon" href="/favicon.ico" sizes="48x48">
  {FONT}
  <link rel="stylesheet" href="/css/style.css">
  <link rel="stylesheet" href="/css/blog.css">
</head>
<body class="blog">
{nav("blog").replace('aria-current="page" class="is-current"', '')}
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
{footer("blog")}
  <script src="/js/main.js"></script>
</body>
</html>
'''
open(OUT, "w", encoding="utf-8").write(php + "\n" + body)
print("privacy ok")
