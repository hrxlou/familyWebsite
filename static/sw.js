const CACHE_NAME = 'family-website-v1.1'; // Increment version to bust cache
const urlsToCache = [
  '/',
  '/style.css',
  '/api.js',
  '/auth.js',
  '/shared.js',
  '/index.html'
];

self.addEventListener('install', event => {
  self.skipWaiting(); // Force active immediately
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.filter(cacheName => cacheName !== CACHE_NAME)
          .map(cacheName => caches.delete(cacheName))
      );
    })
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Update cache with the latest version from network
        const resClone = response.clone();
        caches.open(CACHE_NAME).then(cache => {
          cache.put(event.request, resClone);
        });
        return response;
      })
      .catch(() => caches.match(event.request)) // Fallback to cache if network fails
  );
});
