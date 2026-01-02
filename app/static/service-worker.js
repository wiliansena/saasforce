const CACHE_NAME = "saasfx-static-v1";

// Apenas arquivos estáticos (opcional ir adicionando depois)
const STATIC_ASSETS = [
  "/static/manifest.json",
  "/static/images/icon-192.png",
  "/static/images/icon-512.png",
];

// --------------------
// INSTALL
// --------------------
self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(STATIC_ASSETS);
    })
  );
  self.skipWaiting();
});

// --------------------
// ACTIVATE
// --------------------
self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(k => k !== CACHE_NAME)
          .map(k => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

// --------------------
// FETCH
// --------------------
self.addEventListener("fetch", event => {

  // 🔒 nunca interferir em POST (login, CSRF, formulários)
  if (event.request.method !== "GET") {
    return;
  }

  const url = new URL(event.request.url);

  // 🚫 NÃO cachear rotas do sistema
  if (!url.pathname.startsWith("/static/")) {
    return;
  }

  // ✅ cache-first somente para /static
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});
