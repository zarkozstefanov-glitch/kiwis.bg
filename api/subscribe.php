<?php
/* POST /api/subscribe.php  {first, last, email, consent, website(honeypot), t(ms since the form opened)}
 * Stores the sign-up encrypted as "pending" and sends a confirmation link (double opt-in). */
declare(strict_types=1);
require __DIR__ . '/_lib.php';
k_security_headers();

if ($_SERVER['REQUEST_METHOD'] !== 'POST') k_json(['ok' => false], 405);

// same-site requests only
$origin = $_SERVER['HTTP_ORIGIN'] ?? '';
$host = $_SERVER['HTTP_HOST'] ?? '';
if ($origin !== '' && parse_url($origin, PHP_URL_HOST) !== $host) k_json(['ok' => false], 403);

$in = json_decode(file_get_contents('php://input') ?: '', true);
if (!is_array($in)) k_json(['ok' => false, 'error' => 'bad_request'], 400);

// bots: hidden field filled in, or the form sent faster than a person can type
if (!empty($in['website']) || (int)($in['t'] ?? 0) < 2500) k_json(['ok' => true]);

$clean = fn($v) => trim(preg_replace('/\s+/u', ' ', (string)$v));
$first = $clean($in['first'] ?? '');
$last = $clean($in['last'] ?? '');
$email = mb_strtolower($clean($in['email'] ?? ''));
$errors = [];
$nameOk = fn($n) => $n !== '' && mb_strlen($n) <= 60 && preg_match("/^[\\p{L}][\\p{L} .'\\-]*$/u", $n);
if (!$nameOk($first)) $errors[] = 'first';
if (!$nameOk($last)) $errors[] = 'last';
if (mb_strlen($email) > 160 || !filter_var($email, FILTER_VALIDATE_EMAIL)) $errors[] = 'email';
if (($in['consent'] ?? false) !== true) $errors[] = 'consent';
if ($errors) k_json(['ok' => false, 'error' => 'invalid', 'fields' => $errors], 422);

if (!k_rate_ok('subscribe', 5, 3600)) k_json(['ok' => false, 'error' => 'rate'], 429);

$db = k_db();
$idx = k_index('email:' . $email);
$s = $db->prepare('SELECT id, status FROM subscribers WHERE email_idx = ?');
$s->execute([$idx]);
$row = $s->fetch();
if ($row && $row['status'] === 'confirmed') k_json(['ok' => true]);   // already in — don't reveal it

$token = bin2hex(random_bytes(24));
$now = time();
$data = k_encrypt(['first' => $first, 'last' => $last, 'email' => $email]);
if ($row) {
    $db->prepare('UPDATE subscribers SET data = ?, consent_text = ?, consent_at = ?, ip_hash = ?, confirm_hash = ?, confirm_expires = ? WHERE id = ?')
       ->execute([$data, KIWIS_CONSENT_TEXT, $now, k_ip_hash(), hash('sha256', $token), $now + 172800, $row['id']]);
} else {
    $db->prepare('INSERT INTO subscribers(email_idx, data, status, consent_text, consent_at, ip_hash, confirm_hash, confirm_expires, created_at)
                  VALUES(?, ?, "pending", ?, ?, ?, ?, ?, ?)')
       ->execute([$idx, $data, KIWIS_CONSENT_TEXT, $now, k_ip_hash(), hash('sha256', $token), $now + 172800, $now]);
}

$link = KIWIS_SITE . '/api/confirm.php?t=' . $token;
$hi = 'Здравей, ' . $first . '!';
$text = "$hi\n\nПотвърди, че искаш да получаваш новини и промоции от Kiwi's:\n$link\n\nЛинкът е валиден 48 часа. Ако не си се записвал/а ти, просто игнорирай този имейл — няма да ти пишем.\n\nKiwi's · ул. „Никола Карев“ 14, Пловдив";
$html = k_mail_layout($hi,
    '<p style="line-height:1.55">Потвърди, че искаш да получаваш новини и промоции от Kiwi\'s.</p>'
    . k_btn($link, 'Потвърждавам')
    . '<p style="font-size:13px;color:#4A3F34;line-height:1.5">Линкът е валиден 48 часа. Ако не си се записвал/а ти, просто игнорирай този имейл — няма да ти пишем.</p>');
k_mail($email, "Потвърди записването си в Kiwi's", $text, $html);

k_json(['ok' => true]);
