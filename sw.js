
const CACHE_NAME = 'radar-cloud-v3';
// 关键页面/数据: 永远走网络(绕缓存), 离线时 fallback 缓存
const NO_CACHE = ['app.html', 'index.html', '/data/', 'version.txt', 'manifest.webmanifest'];
self.addEventListener('install', (e) => {
  e.waitUntil(caches.open(CACHE_NAME).then((c) => c.addAll(['./', './data/stats.json'])));
  self.skipWaiting();
});
self.addEventListener('activate', (e) => {
  e.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener('fetch', (e) => {
  const url = e.request.url;
  const isCritical = NO_CACHE.some((k) => url.includes(k));
  if (isCritical) {
    // network-first: 关键数据永远拿最新
    e.respondWith(
      fetch(e.request, { cache: 'no-store' })
        .then((res) => res)
        .catch(() => caches.match(e.request))
    );
    return;
  }
  e.respondWith(
    caches.match(e.request).then((cached) => cached || fetch(e.request).then((res) => {
      if (res.ok) {
        const copy = res.clone();
        caches.open(CACHE_NAME).then((c) => c.put(e.request, copy));
      }
      return res;
    }).catch(() => caches.match('./')))
  );
});
