<?php
/* /api/leave.php — unsubscribe from the website: enter your email, we send the personal
 * unsubscribe link to it (so nobody can remove someone else). */
declare(strict_types=1);
require __DIR__ . '/_lib.php';
k_security_headers();
session_name('kiwis_leave');
session_set_cookie_params(['path' => '/api/', 'httponly' => true, 'samesite' => 'Strict', 'secure' => (($_SERVER['HTTPS'] ?? '') === 'on')]);
session_start();
if (empty($_SESSION['csrf'])) $_SESSION['csrf'] = bin2hex(random_bytes(16));
$sent = false; $err = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $email = mb_strtolower(trim((string)($_POST['email'] ?? '')));
    if (!hash_equals($_SESSION['csrf'], (string)($_POST['csrf'] ?? ''))) $err = 'Опитай отново.';
    elseif (!filter_var($email, FILTER_VALIDATE_EMAIL)) $err = 'Невалиден имейл.';
    elseif (!k_rate_ok('leave', 5, 3600)) $err = 'Твърде много опити. Опитай по-късно.';
    else {
        $s = k_db()->prepare('SELECT id FROM subscribers WHERE email_idx = ?');
        $s->execute([k_index('email:' . $email)]);
        if ($id = $s->fetchColumn()) {
            $link = k_unsub_link((int)$id);
            k_mail($email, "Отписване от имейлите на Kiwi's", "За да се отпишеш и да изтрием данните ти, отвори:\n$link",
                k_mail_layout('Отписване', '<p style="line-height:1.55">Натисни бутона, за да се отпишеш. Ще изтрием името и имейла ти.</p>' . k_btn($link, 'Отпиши ме')));
        }
        $sent = true;
    }
}
header('Content-Type: text/html; charset=utf-8');
$h = fn($s) => htmlspecialchars((string)$s, ENT_QUOTES);
?><!doctype html>
<html lang="bg"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex">
<title>Отписване — Kiwi's</title>
<style>body{margin:0;min-height:100vh;display:grid;place-items:center;background:#1A2D1E;color:#FAF6F0;font-family:system-ui,Arial,sans-serif;padding:20px}
.c{max-width:420px;width:100%;text-align:center}h1{font-family:Georgia,serif;font-size:1.7rem}p{color:rgba(250,246,240,.75);line-height:1.5}
input{width:100%;padding:13px 14px;border-radius:12px;border:1px solid rgba(255,255,255,.2);background:rgba(255,255,255,.08);color:#fff;font:inherit;font-size:16px;box-sizing:border-box}
button,a.b{display:inline-block;margin-top:14px;background:#FFC244;color:#1A1612;border:0;border-radius:40px;padding:13px 26px;font-weight:700;font-size:1rem;cursor:pointer;text-decoration:none}
.e{color:#FFD2C4}</style></head>
<body><div class="c">
<?php if ($sent): ?>
  <h1>Провери пощата си</h1><p>Ако този имейл е записан при нас, изпратихме линк за отписване. С него данните ти се изтриват веднага.</p><a class="b" href="/">Към сайта</a>
<?php else: ?>
  <h1>Отписване</h1><p>Въведи имейла, с който си се записал/а. Ще ти изпратим линк за отписване.</p>
  <?php if ($err): ?><p class="e"><?= $h($err) ?></p><?php endif; ?>
  <form method="post"><input type="hidden" name="csrf" value="<?= $h($_SESSION['csrf']) ?>"><input type="email" name="email" required placeholder="имейл" autocomplete="email"><button>Изпрати линк</button></form>
<?php endif; ?>
</div></body></html>
