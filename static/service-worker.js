self.addEventListener('install', event => {
  event.waitUntil(
    caches.open('supermarket-cache').then(cache => {
      return cache.addAll([
        '/',
        '/static/icons/icon1.png',
        '/static/icons/icon2.png',
        '/static/icons/icon3.png'
      ]);
    })
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});