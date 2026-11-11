/* Kiwi's service worker — the first visit loads everything, the next ones open instantly.
   - pages: shown from the cache right away and refreshed in the background; after 12 h the
     network is tried first, so a new day starts with the newest version
   - css / js / fonts / images: cache first (their URLs change when the file changes: ?v=hash)
   - /api/ and /admin/ are never touched */
const V = '__V__';
const PAGES = 'kiwis-pages-' + V, ASSETS = 'kiwis-assets-v1', FRESH = 12 * 3600 * 1000;

self.addEventListener('install', e => {
  e.waitUntil(caches.open(PAGES).then(c => c.addAll(['/', '/menu.html'])).catch(() => {}).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k.startsWith('kiwis-pages-') && k !== PAGES).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

const stamp = res => {                       // remember when a page was fetched
  const h = new Headers(res.headers); h.set('x-kiwis-at', String(Date.now()));
  return res.blob().then(b => new Response(b, { status: res.status, statusText: res.statusText, headers: h }));
};

self.addEventListener('fetch', e => {
  const req = e.request, url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== location.origin || /^\/(api|admin)\//.test(url.pathname)) return;

  if (req.mode === 'navigate') {
    const key = url.pathname === '/index.html' ? '/' : url.pathname;
    e.respondWith(caches.open(PAGES).then(async c => {
      const cached = await c.match(key);
      const net = fetch(req).then(async r => { if (r.ok && r.type === 'basic') await c.put(key, await stamp(r.clone())); return r; });
      const age = cached ? Date.now() - Number(cached.headers.get('x-kiwis-at') || 0) : Infinity;
      if (cached && age < FRESH) { e.waitUntil(net.catch(() => {})); return cached; }
      return net.catch(() => cached || caches.match('/'));
    }));
    return;
  }

  if (/^\/(css|js|fonts|images)\//.test(url.pathname)) {
    e.respondWith(caches.open(ASSETS).then(async c => {
      const hit = await c.match(req);
      if (hit) return hit;
      const r = await fetch(req);
      if (r.ok && r.type === 'basic') c.put(req, r.clone());
      return r;
    }));
  }
});
