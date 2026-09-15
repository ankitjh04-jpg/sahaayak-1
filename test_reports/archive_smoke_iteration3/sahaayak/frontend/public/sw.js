/* Private API responses, map tiles, and external requests are never cached. */
const CACHE = 'sahaayak-shell-v1';
self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(['/', '/images/wheat-hero.jpg'])).then(() => self.skipWaiting()));
});
self.addEventListener('activate', event => {
  event.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(key => key.startsWith('sahaayak-shell-') && key !== CACHE).map(key => caches.delete(key)))).then(() => self.clients.claim()));
});
function allowed(url) {
  const parsed = new URL(url, self.location.origin);
  return parsed.origin === self.location.origin && !parsed.pathname.startsWith('/api/') && !parsed.pathname.includes('hot-update') && !parsed.pathname.includes('/ws') && !parsed.pathname.endsWith('.map');
}
self.addEventListener('message', event => {
  if(event.data?.type === 'CACHE_APP') event.waitUntil(caches.open(CACHE).then(cache => Promise.all((event.data.urls || []).filter(allowed).map(url => cache.add(url).catch(() => {})))));
});
self.addEventListener('fetch', event => {
  const request = event.request;
  if(request.method !== 'GET' || !allowed(request.url)) return;
  if(request.mode === 'navigate') {
    event.respondWith(fetch(request).then(response => {
      if(response.ok) {const copy = response.clone(); caches.open(CACHE).then(cache => cache.put('/', copy));}
      return response;
    }).catch(() => caches.match('/')));
  } else if(new URL(request.url).pathname.match(/\.(js|css|jpg|png|woff2)$/)) {
    event.respondWith(fetch(request).then(response => {
      if(response.ok) {const copy = response.clone(); caches.open(CACHE).then(cache => cache.put(request, copy));}
      return response;
    }).catch(() => caches.match(request)));
  }
});