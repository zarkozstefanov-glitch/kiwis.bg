<?php
/* Kiwi's — newsletter backend (shared by api/*.php and admin/).
 *
 * Storage: SQLite + key file in a private folder OUTSIDE the web root
 *   (/home/<account>/kiwis-private on SuperHosting), created on first use with 0700/0600 rights.
 * Personal data (first name, last name, email) is encrypted with libsodium (XSalsa20-Poly1305);
 * duplicates are found through a keyed hash of the email (blind index), never the plain email.
 * Nothing here is reachable directly: .htaccess denies files starting with "_".
 */
declare(strict_types=1);

const KIWIS_SITE = 'https://kiwis.bg';
const KIWIS_FROM = "Kiwi's <no-reply@kiwis.bg>";
const KIWIS_FROM_ADDR = 'no-reply@kiwis.bg';
// official Kiwi's email: shown in the privacy notice, receives replies and admin login links
const KIWIS_CONTACT = 'kiwisplovdiv@gmail.com';
// The admin panel answers only from these addresses (anything else gets a plain 404).
const KIWIS_ADMIN_IPS = ['91.148.131.144'];
const KIWIS_CONSENT_TEXT = "Съгласен/на съм Kiwi's да ми изпраща имейли с новини и промоции. Мога да се отпиша по всяко време.";

function k_private_dir(): string {
    $d = getenv('KIWIS_PRIVATE') ?: dirname($_SERVER['DOCUMENT_ROOT'] ?? __DIR__ . '/..') . '/kiwis-private';
    if (!is_dir($d) && !@mkdir($d, 0700, true)) {
        // hosting without write access above the web root: fall back to a folder Apache refuses to serve
        $d = __DIR__ . '/_private';
        if (!is_dir($d)) { mkdir($d, 0700, true); }
    }
    if (!is_file("$d/.htaccess")) { file_put_contents("$d/.htaccess", "Require all denied\n"); }
    return $d;
}

function k_master_key(): string {
    static $key = null;
    if ($key !== null) return $key;
    $f = k_private_dir() . '/key.bin';
    if (!is_file($f)) {
        $tmp = $f . '.' . bin2hex(random_bytes(4));
        file_put_contents($tmp, sodium_crypto_kdf_keygen());
        chmod($tmp, 0600);
        if (!@rename($tmp, $f)) { @unlink($tmp); }        // another request won the race
    }
    $key = file_get_contents($f);
    if (strlen($key) !== SODIUM_CRYPTO_KDF_KEYBYTES) { throw new RuntimeException('bad key'); }
    return $key;
}

function k_subkey(int $id, string $ctx): string {
    return sodium_crypto_kdf_derive_from_key(32, $id, $ctx, k_master_key());
}

function k_encrypt(array $data): string {
    $nonce = random_bytes(SODIUM_CRYPTO_SECRETBOX_NONCEBYTES);
    return $nonce . sodium_crypto_secretbox(json_encode($data, JSON_UNESCAPED_UNICODE), $nonce, k_subkey(1, 'kiwisenc'));
}

function k_decrypt(string $blob): ?array {
    $nonce = substr($blob, 0, SODIUM_CRYPTO_SECRETBOX_NONCEBYTES);
    $plain = sodium_crypto_secretbox_open(substr($blob, SODIUM_CRYPTO_SECRETBOX_NONCEBYTES), $nonce, k_subkey(1, 'kiwisenc'));
    return $plain === false ? null : json_decode($plain, true);
}

function k_index(string $value): string {               // keyed hash: same input -> same value, not reversible
    return bin2hex(sodium_crypto_generichash($value, k_subkey(2, 'kiwisidx'), 32));
}

function k_ip_hash(): string {
    return substr(k_index('ip:' . ($_SERVER['REMOTE_ADDR'] ?? '')), 0, 32);
}

function k_db(): PDO {
    static $db = null;
    if ($db) return $db;
    $f = k_private_dir() . '/kiwis.sqlite';
    $new = !is_file($f);
    $db = new PDO('sqlite:' . $f, null, null, [PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION, PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC]);
    if ($new) { @chmod($f, 0600); }
    $db->exec('PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON; PRAGMA busy_timeout=4000;');
    $db->exec('CREATE TABLE IF NOT EXISTS subscribers (
        id INTEGER PRIMARY KEY,
        email_idx TEXT NOT NULL UNIQUE,
        data BLOB NOT NULL,
        status TEXT NOT NULL DEFAULT "pending",
        consent_text TEXT NOT NULL,
        consent_at INTEGER NOT NULL,
        ip_hash TEXT NOT NULL,
        confirm_hash TEXT,
        confirm_expires INTEGER,
        confirmed_at INTEGER,
        created_at INTEGER NOT NULL)');
    $db->exec('CREATE TABLE IF NOT EXISTS hits (ip_hash TEXT NOT NULL, kind TEXT NOT NULL, ts INTEGER NOT NULL)');
    $db->exec('CREATE INDEX IF NOT EXISTS hits_ip ON hits(ip_hash, kind, ts)');
    $db->exec('CREATE TABLE IF NOT EXISTS admin_tokens (hash TEXT PRIMARY KEY, expires INTEGER NOT NULL)');
    $db->exec('CREATE TABLE IF NOT EXISTS settings (k TEXT PRIMARY KEY, v TEXT NOT NULL)');
    // data minimisation: unconfirmed sign-ups are removed after 48 h, rate-limit hits after a day
    $db->prepare('DELETE FROM subscribers WHERE status = "pending" AND confirm_expires < ?')->execute([time()]);
    $db->prepare('DELETE FROM hits WHERE ts < ?')->execute([time() - 86400]);
    $db->prepare('DELETE FROM admin_tokens WHERE expires < ?')->execute([time()]);
    return $db;
}

function k_setting(string $k, ?string $default = null): ?string {
    $s = k_db()->prepare('SELECT v FROM settings WHERE k = ?'); $s->execute([$k]);
    $v = $s->fetchColumn();
    return $v === false ? $default : $v;
}

function k_set_setting(string $k, string $v): void {
    k_db()->prepare('INSERT INTO settings(k, v) VALUES(?, ?) ON CONFLICT(k) DO UPDATE SET v = excluded.v')->execute([$k, $v]);
}

/* true when this IP did $kind fewer than $max times in the last $window seconds (and records the hit) */
function k_rate_ok(string $kind, int $max, int $window): bool {
    $db = k_db(); $ip = k_ip_hash();
    $s = $db->prepare('SELECT COUNT(*) FROM hits WHERE ip_hash = ? AND kind = ? AND ts > ?');
    $s->execute([$ip, $kind, time() - $window]);
    if ((int)$s->fetchColumn() >= $max) return false;
    $db->prepare('INSERT INTO hits(ip_hash, kind, ts) VALUES(?, ?, ?)')->execute([$ip, $kind, time()]);
    return true;
}

function k_mail(string $to, string $subject, string $text, string $html): bool {
    $b = 'kiwis' . bin2hex(random_bytes(8));
    $headers = implode("\r\n", [
        'From: ' . '=?UTF-8?B?' . base64_encode("Kiwi's") . '?= <' . KIWIS_FROM_ADDR . '>',
        'Reply-To: ' . KIWIS_CONTACT,
        'MIME-Version: 1.0',
        "Content-Type: multipart/alternative; boundary=\"$b\"",
    ]);
    $body = "--$b\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: base64\r\n\r\n" . chunk_split(base64_encode($text))
          . "--$b\r\nContent-Type: text/html; charset=UTF-8\r\nContent-Transfer-Encoding: base64\r\n\r\n" . chunk_split(base64_encode($html))
          . "--$b--\r\n";
    if (getenv('KIWIS_MAIL_LOG')) {                       // local testing: write mails to a file instead
        file_put_contents(getenv('KIWIS_MAIL_LOG'), "TO: $to\nSUBJECT: $subject\n$text\n-----\n", FILE_APPEND);
        return true;
    }
    return mail($to, '=?UTF-8?B?' . base64_encode($subject) . '?=', $body, $headers, '-f' . KIWIS_FROM_ADDR);
}

function k_mail_layout(string $title, string $bodyHtml): string {
    return '<!doctype html><html lang="bg"><body style="margin:0;background:#FAF6F0;font-family:Arial,Helvetica,sans-serif;color:#1A1612">'
         . '<div style="max-width:520px;margin:0 auto;padding:28px 20px">'
         . '<div style="background:#1A2D1E;color:#FAF6F0;border-radius:18px 18px 0 0;padding:22px 26px;font-size:22px;font-weight:bold">KiWi\'S</div>'
         . '<div style="background:#ffffff;border-radius:0 0 18px 18px;padding:26px">'
         . '<h1 style="font-size:20px;margin:0 0 12px;color:#1A2D1E">' . htmlspecialchars($title) . '</h1>' . $bodyHtml . '</div>'
         . '<p style="font-size:12px;color:#8A7E72;text-align:center;margin-top:16px">Kiwi\'s · ул. „Никола Карев“ 14, Пловдив · +359 892 632 470</p>'
         . '</div></body></html>';
}

function k_btn(string $href, string $label): string {
    return '<p style="margin:22px 0"><a href="' . htmlspecialchars($href) . '" style="background:#FFC244;color:#1A1612;text-decoration:none;font-weight:bold;padding:13px 26px;border-radius:40px;display:inline-block">' . htmlspecialchars($label) . '</a></p>';
}

function k_unsub_link(int $id): string {
    $t = substr(k_index('unsub:' . $id), 0, 40);
    return KIWIS_SITE . '/api/unsubscribe.php?id=' . $id . '&t=' . $t;
}

function k_json(array $data, int $code = 200): never {
    http_response_code($code);
    header('Content-Type: application/json; charset=utf-8');
    header('Cache-Control: no-store');
    echo json_encode($data, JSON_UNESCAPED_UNICODE);
    exit;
}

function k_security_headers(): void {
    header('X-Content-Type-Options: nosniff');
    header('Referrer-Policy: same-origin');
    header('X-Frame-Options: DENY');
    header('Cache-Control: no-store');
}
