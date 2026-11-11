<?php
/* Kiwi's admin — subscribers.
 * - answers only from KIWIS_ADMIN_IPS (everything else gets the normal 404 page)
 * - first visit: set the admin email; afterwards login is a one-time link sent to that email (15 min)
 * - session cookie: Secure, HttpOnly, SameSite=Strict, bound to the IP, 12 h */
declare(strict_types=1);
require __DIR__ . '/../api/_lib.php';
k_security_headers();
header("Content-Security-Policy: default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; form-action 'self'; frame-ancestors 'none'");
header('X-Robots-Tag: noindex, nofollow');

$allowed = array_merge(KIWIS_ADMIN_IPS, array_filter(explode(',', (string)getenv('KIWIS_ADMIN_IPS_EXTRA'))));   // env: local testing only
if (!in_array($_SERVER['REMOTE_ADDR'] ?? '', $allowed, true)) {
    http_response_code(404);
    readfile(__DIR__ . '/../404.html');
    exit;
}

$secure = (($_SERVER['HTTPS'] ?? '') === 'on') || (($_SERVER['HTTP_X_FORWARDED_PROTO'] ?? '') === 'https');
session_name('kiwis_admin');
session_set_cookie_params(['lifetime' => 0, 'path' => '/admin/', 'secure' => $secure, 'httponly' => true, 'samesite' => 'Strict']);
session_start();

$h = fn($s) => htmlspecialchars((string)$s, ENT_QUOTES);
$self = '/admin/';
$msg = '';
$adminEmail = k_setting('admin_email', KIWIS_CONTACT);
$logged = !empty($_SESSION['ok']) && ($_SESSION['ip'] ?? '') === ($_SERVER['REMOTE_ADDR'] ?? '') && ($_SESSION['until'] ?? 0) > time();
if (empty($_SESSION['csrf'])) $_SESSION['csrf'] = bin2hex(random_bytes(16));
$csrfOk = fn() => hash_equals($_SESSION['csrf'], (string)($_POST['csrf'] ?? ''));
$db = k_db();

// ---- one-time login link
if (isset($_GET['login'])) {
    $s = $db->prepare('SELECT hash FROM admin_tokens WHERE hash = ? AND expires >= ?');
    $s->execute([hash('sha256', (string)$_GET['login']), time()]);
    if ($s->fetchColumn()) {
        $db->prepare('DELETE FROM admin_tokens WHERE hash = ?')->execute([hash('sha256', (string)$_GET['login'])]);
        session_regenerate_id(true);
        $_SESSION = ['ok' => 1, 'ip' => $_SERVER['REMOTE_ADDR'], 'until' => time() + 43200, 'csrf' => bin2hex(random_bytes(16))];
        header('Location: ' . $self, true, 303); exit;
    }
    $msg = 'Линкът е изтекъл или вече е използван. Поискай нов.';
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && $csrfOk()) {
    $act = $_POST['act'] ?? '';
    if ($act === 'setup' && !$adminEmail) {
        $e = mb_strtolower(trim((string)($_POST['email'] ?? '')));
        if (filter_var($e, FILTER_VALIDATE_EMAIL)) { k_set_setting('admin_email', $e); $adminEmail = $e; $msg = 'Имейлът е запазен. Сега поискай линк за вход.'; }
        else $msg = 'Невалиден имейл.';
    } elseif ($act === 'link' && $adminEmail) {
        $e = mb_strtolower(trim((string)($_POST['email'] ?? '')));
        if (k_rate_ok('adminlink', 5, 3600) && hash_equals($adminEmail, $e)) {
            $tok = bin2hex(random_bytes(24));
            $db->prepare('INSERT INTO admin_tokens(hash, expires) VALUES(?, ?)')->execute([hash('sha256', $tok), time() + 900]);
            $link = KIWIS_SITE . $self . '?login=' . $tok;
            k_mail($adminEmail, "Вход в админ панела на Kiwi's", "Линк за вход (валиден 15 минути, само веднъж):\n$link",
                k_mail_layout('Вход в админ панела', '<p>Линкът е валиден 15 минути и може да се използва веднъж.</p>' . k_btn($link, 'Влез')));
        }
        $msg = 'Ако имейлът е правилен, изпратихме линк за вход. Провери пощата си.';
    } elseif ($logged && $act === 'delete') {
        $db->prepare('DELETE FROM subscribers WHERE id = ?')->execute([(int)($_POST['id'] ?? 0)]);
        $msg = 'Записът е изтрит.';
    } elseif ($logged && $act === 'settings') {
                $e = mb_strtolower(trim((string)($_POST['admin_email'] ?? '')));
        if (filter_var($e, FILTER_VALIDATE_EMAIL)) { k_set_setting('admin_email', $e); $adminEmail = $e; }
        $msg = 'Настройките са запазени.';
    } elseif ($act === 'logout') {
        $_SESSION = []; session_destroy();
        header('Location: ' . $self, true, 303); exit;
    }
}

// ---- CSV export (confirmed subscribers)
if ($logged && ($_GET['export'] ?? '') === 'csv') {
    header('Content-Type: text/csv; charset=utf-8');
    header('Content-Disposition: attachment; filename="kiwis-subscribers-' . date('Y-m-d') . '.csv"');
    $out = fopen('php://output', 'w');
    fwrite($out, "\xEF\xBB\xBF");
    fputcsv($out, ['first_name', 'last_name', 'email', 'confirmed_at', 'consent_at', 'unsubscribe_link'], ',', '"', '');
    foreach ($db->query('SELECT * FROM subscribers WHERE status = "confirmed" ORDER BY confirmed_at') as $r) {
        $d = k_decrypt($r['data']); if (!$d) continue;
        fputcsv($out, [$d['first'], $d['last'], $d['email'], date('Y-m-d H:i', (int)$r['confirmed_at']), date('Y-m-d H:i', (int)$r['consent_at']), k_unsub_link((int)$r['id'])], ',', '"', '');
    }
    exit;
}

header('Content-Type: text/html; charset=utf-8');
?><!doctype html>
<html lang="bg"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex, nofollow">
<title>Админ — Kiwi's</title>
<style>
:root{--f:#1A2D1E;--s:#FFC244;--c:#FAF6F0;--i:#1A1612}
*{box-sizing:border-box}body{margin:0;background:var(--c);color:var(--i);font-family:system-ui,-apple-system,Segoe UI,Arial,sans-serif}
header{background:var(--f);color:var(--c);padding:16px 24px;display:flex;align-items:center;justify-content:space-between;gap:12px}
header b{font-family:Georgia,serif;font-size:1.3rem}main{max-width:1100px;margin:0 auto;padding:24px}
.card{background:#fff;border-radius:16px;padding:20px;box-shadow:0 10px 30px -22px rgba(26,45,30,.5);margin-bottom:18px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px}.stat b{display:block;font-size:2rem;font-family:Georgia,serif;color:var(--f)}
table{width:100%;border-collapse:collapse;font-size:.92rem}th,td{text-align:left;padding:10px 8px;border-bottom:1px solid #eee;vertical-align:middle}th{color:#6b6156;font-weight:600}
input[type=email],input[type=text]{width:100%;padding:11px 12px;border:1px solid #d9d2c6;border-radius:10px;font:inherit}
label{display:block;font-size:.85rem;color:#4A3F34;margin:10px 0 4px}
button,.btn{background:var(--s);color:var(--i);border:0;border-radius:40px;padding:10px 18px;font-weight:700;font:inherit;font-weight:700;cursor:pointer;text-decoration:none;display:inline-block}
.btn--ghost{background:transparent;color:var(--c);border:1px solid rgba(250,246,240,.4)}.del{background:#fbe3dc;color:#8a2b12;padding:6px 12px;font-size:.85rem}
.msg{background:#FFE7A8;border-radius:12px;padding:12px 14px;margin-bottom:16px}.pill{font-size:.75rem;padding:3px 9px;border-radius:20px;background:#e6efe7;color:#2e4a32}.pill.p{background:#f1e6d2;color:#7a5a1a}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:0 16px}@media(max-width:700px){.grid2{grid-template-columns:1fr}td,th{font-size:.82rem}}
.login{max-width:420px;margin:60px auto}
</style></head><body>
<header><b>KiWi'S · админ</b><?php if ($logged): ?><form method="post"><input type="hidden" name="csrf" value="<?= $h($_SESSION['csrf']) ?>"><button class="btn btn--ghost" name="act" value="logout">Изход</button></form><?php endif; ?></header>
<main>
<?php if ($msg): ?><div class="msg"><?= $h($msg) ?></div><?php endif; ?>

<?php if (!$adminEmail): ?>
  <div class="card login"><h2>Първоначална настройка</h2><p>Въведи имейла на Kiwi's. На него ще идват линковете за вход в панела.</p>
  <form method="post"><input type="hidden" name="csrf" value="<?= $h($_SESSION['csrf']) ?>"><input type="hidden" name="act" value="setup">
  <label>Имейл</label><input type="email" name="email" required autocomplete="email"><p><button>Запази</button></p></form></div>

<?php elseif (!$logged): ?>
  <div class="card login"><h2>Вход</h2><p>Ще ти изпратим еднократен линк за вход.</p>
  <form method="post"><input type="hidden" name="csrf" value="<?= $h($_SESSION['csrf']) ?>"><input type="hidden" name="act" value="link">
  <label>Имейл на Kiwi's</label><input type="email" name="email" required autocomplete="email"><p><button>Изпрати линк</button></p></form></div>

<?php else:
  $rows = $db->query('SELECT * FROM subscribers ORDER BY created_at DESC')->fetchAll();
  $conf = count(array_filter($rows, fn($r) => $r['status'] === 'confirmed'));
  $pend = count($rows) - $conf;
  $week = count(array_filter($rows, fn($r) => $r['status'] === 'confirmed' && $r['confirmed_at'] > time() - 604800));
?>
  <div class="stats">
    <div class="card stat"><b><?= $conf ?></b>потвърдени абонати</div>
    <div class="card stat"><b><?= $week ?></b>нови за 7 дни</div>
    <div class="card stat"><b><?= $pend ?></b>чакат потвърждение (изтриват се след 48 ч)</div>
  </div>
  <div class="card">
    <div style="display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap"><h2 style="margin:0">Абонати</h2><a class="btn" href="?export=csv">Свали CSV (потвърдени)</a></div>
    <div style="overflow-x:auto"><table><tr><th>Име</th><th>Имейл</th><th>Статус</th><th>Записан</th><th></th></tr>
    <?php foreach ($rows as $r): $d = k_decrypt($r['data']) ?? ['first' => '?', 'last' => '', 'email' => '?']; ?>
      <tr><td><?= $h($d['first'] . ' ' . $d['last']) ?></td><td><?= $h($d['email']) ?></td>
      <td><span class="pill <?= $r['status'] === 'confirmed' ? '' : 'p' ?>"><?= $r['status'] === 'confirmed' ? 'потвърден' : 'чака' ?></span></td>
      <td><?= date('d.m.Y H:i', (int)($r['confirmed_at'] ?: $r['created_at'])) ?></td>
      <td><form method="post" onsubmit="return confirm('Да изтрия ли този абонат завинаги?')"><input type="hidden" name="csrf" value="<?= $h($_SESSION['csrf']) ?>"><input type="hidden" name="id" value="<?= (int)$r['id'] ?>"><button class="del" name="act" value="delete">Изтрий</button></form></td></tr>
    <?php endforeach; if (!$rows): ?><tr><td colspan="5">Все още няма записани.</td></tr><?php endif; ?>
    </table></div>
  </div>
  <div class="card"><h2>Настройки</h2>
  <form method="post"><input type="hidden" name="csrf" value="<?= $h($_SESSION['csrf']) ?>"><input type="hidden" name="act" value="settings">
    <div class="grid2">
      <div><label>Имейл за вход в панела</label><input type="email" name="admin_email" value="<?= $h($adminEmail) ?>"></div>
    </div><p><button>Запази</button></p></form></div>
<?php endif; ?>
</main></body></html>
