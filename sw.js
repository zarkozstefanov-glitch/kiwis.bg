/* Kiwi's service worker.
   - pages: always use the current HTML online; cached pages are only an offline fallback
   - css / js / fonts / images: cache first (their URLs change when the file changes: ?v=hash)
   - /api/ and /admin/ are never touched */
const V = '__V__';
const PAGES = 'kiwis-pages-' + V, ASSETS = 'kiwis-assets-v2';

self.addEventListener('install', e => {
  e.waitUntil(caches.open(PAGES).then(c => c.addAll(['/', '/menu.html'].map(path => new Request(new URL(path, self.location.origin), { cache: 'reload' })))).catch(() => {}).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    const legacy = keys.includes('kiwis-assets-v1');
    await Promise.all(keys.filter(k => (k.startsWith('kiwis-pages-') && k !== PAGES) || (k.startsWith('kiwis-assets-') && k !== ASSETS)).map(k => caches.delete(k)));
    await self.clients.claim();
    // One-time migration: old tabs may already contain the obsolete cached header.
    // Refresh those documents once; future activations do not reload open pages.
    if (legacy) {
      const windows = await self.clients.matchAll({ type: 'window' });
      // Do not await navigation here: WebKit waits for activation to finish first.
      windows.filter(c => !/^\/(api|admin)\//.test(new URL(c.url).pathname)).forEach(c => { c.navigate(c.url).catch(() => {}); });
    }
  })());
});

self.addEventListener('fetch', e => {
  const req = e.request, url = new URL(req.url);
  if (req.method !== 'GET' || url.origin !== location.origin || /^\/(api|admin)\//.test(url.pathname)) return;

  if (req.mode === 'navigate') {
    const key = url.pathname === '/index.html' ? '/' : url.pathname;
    e.respondWith(caches.open(PAGES).then(async c => {
      try {
        const r = await fetch(req, { cache: 'no-cache' });
        if (r.ok && r.type === 'basic') await c.put(key, r.clone()).catch(() => {});
        return r;
      } catch (err) {
        return await c.match(key) || await c.match('/') || Response.error();
      }
    }));
    return;
  }

  if (/^\/(css|js|fonts|images)\//.test(url.pathname)) {
    e.respondWith(caches.open(ASSETS).then(async c => {
      const hit = await c.match(req);
      if (hit) return hit;
      const r = await fetch(req);
      if (r.ok && r.type === 'basic') e.waitUntil(c.put(req, r.clone()).catch(() => {}));
      return r;
    }));
  }
});
