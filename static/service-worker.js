// 📦 service-worker.js（キャッシュ制御の基本）

const CACHE_NAME = "tire-inventory-cache-v1";
const urlsToCache = [
  "/",  // トップページ
  "/static/css/style.css",
  "/static/script.js",
  "/static/icons/icon-192.png",
  "/static/icons/icon-512.png",
  "/manifest.json"
];

// インストール時にキャッシュ
self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(urlsToCache);
    })
  );
});

// リクエスト時にキャッシュを優先
self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});

// 古いキャッシュを削除
self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});