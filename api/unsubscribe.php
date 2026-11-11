<?php
/* GET /api/unsubscribe.php?id=..&t=.. — shows a confirm button; POST deletes the person's data completely. */
declare(strict_types=1);
require __DIR__ . '/_lib.php';
k_security_headers();

$id = (int)($_REQUEST['id'] ?? 0);
$t = (string)($_REQUEST['t'] ?? '');
$valid = $id > 0 && hash_equals(substr(k_index('unsub:' . $id), 0, 40), $t);
$done = false;
if ($valid && $_SERVER['REQUEST_METHOD'] === 'POST') {
    k_db()->prepare('DELETE FROM subscribers WHERE id = ?')->execute([$id]);
    $done = true;
}
header('Content-Type: text/html; charset=utf-8');
?><!doctype html>
<html lang="bg"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex">
<title>Отписване — Kiwi's</title>
<style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#1A2D1E;color:#FAF6F0;font-family:system-ui,Arial,sans-serif;padding:20px}
.c{max-width:420px;text-align:center}h1{font-family:Georgia,serif;font-size:1.7rem}p{color:rgba(250,246,240,.75);line-height:1.5}
button,a.b{display:inline-block;margin-top:14px;background:#FFC244;color:#1A1612;border:0;border-radius:40px;padding:13px 26px;font-weight:700;font-size:1rem;cursor:pointer;text-decoration:none}</style></head>
<body><div class="c">
<?php if ($done): ?>
  <h1>Отписа се</h1><p>Изтрихме името и имейла ти. Няма да получаваш повече имейли от нас.</p><a class="b" href="/">Към сайта</a>
<?php elseif ($valid): ?>
  <h1>Отписване</h1><p>Сигурен/на ли си? Ще изтрием името и имейла ти и няма да ти пишем повече.</p>
  <form method="post"><input type="hidden" name="id" value="<?= $id ?>"><input type="hidden" name="t" value="<?= htmlspecialchars($t) ?>"><button>Да, отпиши ме</button></form>
<?php else: ?>
  <h1>Невалиден линк</h1><p>Линкът за отписване не е валиден или вече е използван.</p><a class="b" href="/">Към сайта</a>
<?php endif; ?>
</div></body></html>
