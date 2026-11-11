<?php
/* GET /api/confirm.php?t=<token> — second step of the double opt-in. */
declare(strict_types=1);
require __DIR__ . '/_lib.php';
k_security_headers();

$t = (string)($_GET['t'] ?? '');
$result = 'invalid';
if (preg_match('/^[a-f0-9]{48}$/', $t)) {
    $db = k_db();
    $s = $db->prepare('SELECT id, data FROM subscribers WHERE confirm_hash = ? AND status = "pending" AND confirm_expires >= ?');
    $s->execute([hash('sha256', $t), time()]);
    if ($row = $s->fetch()) {
        $db->prepare('UPDATE subscribers SET status = "confirmed", confirmed_at = ?, confirm_hash = NULL, confirm_expires = NULL WHERE id = ?')
           ->execute([time(), $row['id']]);
        $result = 'ok';
        $d = k_decrypt($row['data']);
        if ($d) {
            $unsub = k_unsub_link((int)$row['id']);
            $hi = 'Добре дошъл/дошла, ' . $d['first'] . '!';
            k_mail($d['email'], "Вече си част от семейството на Kiwi's",
                "$hi\n\nЗаписахме те. Ще ти пишем, когато имаме нови ястия и промоции.\n\nОтписване: $unsub",
                k_mail_layout($hi, '<p style="line-height:1.55">Записахме те. Ще ти пишем, когато имаме нови ястия и промоции.</p>'
                    . '<p style="font-size:12px;color:#8A7E72">Не искаш повече имейли? <a href="' . htmlspecialchars($unsub) . '" style="color:#3D6344">Отпиши се</a>.</p>'));
        }
    }
}
header('Location: /?joined=' . $result, true, 303);
