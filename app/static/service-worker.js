self.addEventListener("install", () => {
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener("fetch", event => {
  // Não interfere em POST (login / CSRF)
  if (event.request.method !== "GET") {
    return;
  }
});
