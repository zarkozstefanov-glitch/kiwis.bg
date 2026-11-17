# SEO опис — 17.11.2026

## В сайта

- BG и EN имат отделни HTML адреси: `/` и `/en/`, `/menu.html` и `/en/menu.html`, `/blog/` и `/en/blog/`, както и по три статии на всеки език. Поверителността и 404 също имат преводи, но са `noindex`.
- Всяка индексируема страница има собствен canonical, уникални title и description, Open Graph/Twitter мета тагове и взаимни `hreflang="bg"`, `hreflang="en"`, `hreflang="x-default"` връзки. Езиковите бутони и вътрешните линкове сочат към реални HTML адреси.
- `sitemap.xml` съдържа 12 индексируеми адреса и езиковите им алтернативи. Няма автоматично измислена дата `lastmod` при всеки deploy.
- JSON-LD съдържа Restaurant, Menu, Blog/Article, WebSite/WebPage и breadcrumb данни според страницата. Статистиката за Google отзивите не е добавена като `aggregateRating` на собствения сайт.
- Apache пренасочва HTTP, `www` и `index.html` вариантите с 301. `/api/` и `/admin/` са изключени от robots.txt, PHP отговорите получават `X-Robots-Tag: noindex`. Дублиращото Vercel копие също получава `noindex`.
- `./scripts/build.sh` изпълнява проверка за canonical/hreflang, sitemap, вътрешни линкове и валиден JSON-LD. Проверката покрива 16 HTML страници.

## Публични препратки и профили

- [Oink: Kiwi's Пловдив](https://www.oink.bg/biz/kiwis) показва адреса `kiwis.bg` в публичния си резултат. Профилът е означен „Непотвърден“ и показва стар брой отзиви (17 при проверката). Собственикът на профила може да го потвърди и актуализира.
- [Local Bulgaria: ресторанти в Пловдив](https://localbulgaria.net/en/kategoriya/restoranti/plovdiv?page=2) съдържа Kiwi's с правилните адрес и телефон, но показва стар брой отзиви (48 при проверката). Публичният списък не доказва, че профилът дава кликаем линк към сайта.
- В сайта вече има връзки към Google Maps, Facebook, Instagram, Glovo и Bolt Food. За обратни връзки провери дали всеки **външен профил** действително сочи към `https://kiwis.bg/` и към каноничното меню. Промяна във външен профил изисква достъп до съответния акаунт.
- Няма свързан Google Search Console или Bing Webmaster акаунт в тази работна среда. След deploy подай `https://kiwis.bg/sitemap.xml` и провери индексните отчети и Links в Search Console. Не са създавани или заявявани външни обратни връзки от името на бизнеса.

Техническата настройка следва [указанията на Google за езикови версии](https://developers.google.com/search/docs/specialty/international/localized-versions) и [канонични адреси](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls).
