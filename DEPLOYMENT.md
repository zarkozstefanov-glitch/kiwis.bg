# Deployment — kiwis.bg

## 1. Технология
HTML + CSS + JavaScript, с PHP endpoint за бюлетина. Няма framework или `npm` зависимости за build.
Build-ът създава BG и EN версии на началната страница, менюто, статиите, страницата за поверителност и 404.

## 2. Build команда
```bash
./scripts/build.sh
```
Копира само нужните файлове, генерира английски HTML и двуезичен `sitemap.xml`, добавя `?v=<hash>`
към CSS/JS/снимките и проверява SEO адресите, вътрешните линкове, JSON-LD и assets. При проблем build-ът спира.

## 3. Build output
`dist/` — само тази папка се качва на хостинга. (`dist/` не се commit-ва.)

## 4. Автоматичен deploy
`push` към `main` → GitHub Actions (`.github/workflows/deploy.yml`) → `./scripts/build.sh` → FTPS (TLS, порт 21)
→ `public_html/` на `nebula.superhosting.bg`.

Използва се `SamKirkland/FTP-Deploy-Action`: качва само променените файлове и пази състояние в
`public_html/.ftp-deploy-sync-state.json` (блокиран за публичен достъп от `.htaccess`).
Трие само файлове, които самият той е качил преди — други файлове в `public_html` не се пипат.

Същият push deploy-ва и preview копието на Vercel (https://kivis-bg.vercel.app/, вързано с GitHub).
`vercel.json` кара Vercel да пусне същия `scripts/build.sh`, да сервира само `dist/` и да маркира
preview копието с `X-Robots-Tag: noindex, nofollow`. Основният публичен адрес е `https://kiwis.bg/`.

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

## 10. SEO след deploy
- `.htaccess` пренасочва HTTP, `www` и `index.html` вариантите към каноничните адреси. Провери ги с `curl -I`.
- Публичният `https://kiwis.bg/sitemap.xml` съдържа BG/EN адресите и reciprocal `hreflang`.
- Подай sitemap в Google Search Console и Bing Webmaster Tools от акаунта на собственика. Няма свързан акаунт за автоматично подаване.
- Поддържай сайта, менюто, телефона и социалните линкове в Google Business Profile и външните директории.
- Текущият SEO опис и проверката на публичните препратки са в [SEO.md](SEO.md).

## Снимки
Оригиналите (master) са в `assets-src/images/` и **не** се качват. Уеб версиите (WebP 600/1000/1600 + JPG fallback)
са в `images/`. При нова/сменена снимка: сложете master файла в `assets-src/images/` с желаното име и пуснете
```bash
python3 scripts/optimize_images.py   # изисква Pillow: pip3 install Pillow
```
