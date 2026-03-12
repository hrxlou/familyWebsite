const CACHE_NAME = 'family-website-v1';
const urlsToCache = [
  '/',
  '/style.css',
  '/api.js',
  '/auth.js',
  '/shared.js',
  '/index.html'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
  );
});
