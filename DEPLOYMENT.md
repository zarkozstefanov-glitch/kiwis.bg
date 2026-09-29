# Deployment — kiwis.bg

## 1. Технология
Статичен сайт: чист HTML + CSS + JavaScript. Няма framework, няма backend, няма `npm` зависимости.
Страници: `index.html`, `menu.html`, `404.html`.

## 2. Build команда
```bash
./scripts/build.sh
```
Копира само нужните файлове, добавя `?v=<commit>` към CSS/JS (cache-busting), попълва датата в `sitemap.xml`
и проверява за липсващи assets, `localhost`, `http://`, `console.log`, `.env`/`.md` файлове. При проблем build-ът спира.

## 3. Build output
`dist/` — само тази папка се качва на хостинга. (`dist/` не се commit-ва.)

## 4. Автоматичен deploy
`push` към `main` → GitHub Actions (`.github/workflows/deploy.yml`) → `./scripts/build.sh` → FTPS (TLS, порт 21)
→ `public_html/` на `nebula.superhosting.bg`.

Използва се `SamKirkland/FTP-Deploy-Action`: качва само променените файлове и пази състояние в
`public_html/.ftp-deploy-sync-state.json` (блокиран за публичен достъп от `.htaccess`).
Трие само файлове, които самият той е качил преди — други файлове в `public_html` не се пипат.

Същият push deploy-ва и preview копието на Vercel (https://kivis-bg.vercel.app/, вързано с GitHub).
`vercel.json` кара Vercel да пусне същия `scripts/build.sh` и да сервира само `dist/`.

## 5. GitHub Secrets
Repository → Settings → Secrets and variables → Actions → New repository secret:

| Secret | Стойност |
|---|---|
| `SUPERHOSTING_FTP_HOST` | `nebula.superhosting.bg` |
| `SUPERHOSTING_FTP_USERNAME` | `kiwisbgo` |
| `SUPERHOSTING_FTP_PASSWORD` | FTP/cPanel паролата |

Сайтът няма API ключове или environment variables — други secrets не са нужни.

## 6. Къде отиват файловете
`/home/kiwisbgo/public_html/` (`server-dir: ./public_html/`, спрямо root-а на FTP акаунта).
Ако FTP акаунтът ви се логва директно в `public_html`, сменете `server-dir` на `./`.

## 7. Ръчен deploy
- **През GitHub:** Actions → „Deploy to SuperHosting“ → **Run workflow**.
- **Без GitHub:** `./scripts/build.sh`, после качете **съдържанието** на `dist/` (вкл. скрития `.htaccess`)
  в `public_html/` с FileZilla (FTP over explicit TLS, порт 21) или cPanel → File Manager.

## 8. Rollback
```bash
git revert <лош-commit>   # или няколко commit-а
git push origin main      # deploy-ва предишното състояние
```
Алтернатива: Actions → стар успешен run → **Re-run all jobs** (build-ва кода от онзи commit).

## 9. Проверки в SuperHosting / cPanel
- В `public_html` да няма стар `index.php`/`default.html` на хостинга (той може да има приоритет) — изтрийте го.
- cPanel → SSL/TLS Status → AutoSSL да е издал сертификат за `kiwis.bg` и `www.kiwis.bg`.
- Ако deploy-ът не може да се свърже: проверете дали FTP паролата е вярна и дали FTPS не е блокиран.

## 10. След като kiwis.bg се активира
1. Изчакайте AutoSSL да издаде сертификат и проверете `https://kiwis.bg/`.
2. В `.htaccess` разкоментирайте трите реда под „HTTPS + non-www“ и push-нете → всички http/www заявки
   се пренасочват към `https://kiwis.bg`.
3. Google Search Console: добавете `kiwis.bg` (Domain property), подайте `https://kiwis.bg/sitemap.xml`.
4. Bing Webmaster Tools: импорт от Search Console (Bing захранва ChatGPT/Copilot търсенето).
5. Google Business Profile: създайте/верифицирайте „Kiwi's“ с адрес ул. Никола Карев 14, Пловдив,
   работно време, телефон, сайт `https://kiwis.bg/`, линк към менюто и снимки. Това е най-важното за „в Пловдив“ търсения и Google Maps.
6. Проверете structured data: https://search.google.com/test/rich-results
7. Добавете линк към Instagram/Facebook профила в JSON-LD (`sameAs` в `index.html`) щом имате финалните URL-и.

## Снимки
Оригиналите (master) са в `assets-src/images/` и **не** се качват. Уеб версиите (WebP 600/1000/1600 + JPG fallback)
са в `images/`. При нова/сменена снимка: сложете master файла в `assets-src/images/` с желаното име и пуснете
```bash
python3 scripts/optimize_images.py   # изисква Pillow: pip3 install Pillow
```
