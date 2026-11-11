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
if ($row && $row['status'] === 'confirmed') k_json(['ok' => true, 'already' => true]);

$now = time();
$data = k_encrypt(['first' => $first, 'last' => $last, 'email' => $email]);
// single opt-in: the ticked consent box is the consent — the person is subscribed right away
if ($row) {
    $db->prepare('UPDATE subscribers SET data = ?, status = "confirmed", consent_text = ?, consent_at = ?, ip_hash = ?, confirm_hash = NULL, confirm_expires = NULL, confirmed_at = ? WHERE id = ?')
       ->execute([$data, KIWIS_CONSENT_TEXT, $now, k_ip_hash(), $now, $row['id']]);
    $id = (int)$row['id'];
} else {
    $db->prepare('INSERT INTO subscribers(email_idx, data, status, consent_text, consent_at, ip_hash, confirmed_at, created_at)
                  VALUES(?, ?, "confirmed", ?, ?, ?, ?, ?)')
       ->execute([$idx, $data, KIWIS_CONSENT_TEXT, $now, k_ip_hash(), $now, $now]);
    $id = (int)$db->lastInsertId();
}

// welcome email with the unsubscribe link (also tells the owner of the address, if someone else typed it)
$unsub = k_unsub_link($id);
$hi = 'Добре дошъл/дошла, ' . $first . '!';
k_mail($email, "Вече си част от семейството на Kiwi's",
    "$hi\n\nЗаписахме те за новини и промоции от Kiwi's.\n\nНе си се записвал/а ти или не искаш повече имейли? Отписване: $unsub\n\nKiwi's · ул. „Никола Карев“ 14, Пловдив",
    k_mail_layout($hi, '<p style="line-height:1.55">Записахме те за новини и промоции от Kiwi\'s. Ще ти пишем, когато имаме нови ястия и оферти.</p>'
        . '<p style="font-size:12px;color:#8A7E72">Не си се записвал/а ти или не искаш повече имейли? <a href="' . htmlspecialchars($unsub) . '" style="color:#3D6344">Отпиши се</a>.</p>'));

k_json(['ok' => true]);
