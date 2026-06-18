const CACHE_NAME = 'iflash-v1';
const ASSETS = [
  '/',
  '/static/manifest.json'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', e => {
  // Sempre busca da rede primeiro (sistema precisa de dados atualizados)
  e.respondWith(
    fetch(e.request).catch(() => caches.match(e.request))
  );
});
