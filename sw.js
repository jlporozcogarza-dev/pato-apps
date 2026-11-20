/* Service worker de JLP: SOLO notificaciones (avisos de la Cam). No guarda nada en caché, así el app siempre se actualiza normal. */
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", e => e.waitUntil(self.clients.claim()));

self.addEventListener("push", e => {
  let d = {};
  try{ d = e.data ? e.data.json() : {}; }catch(_){ d = { body:e.data ? e.data.text() : "" }; }
  e.waitUntil(self.registration.showNotification(d.title || "JLP", {
    body:d.body || "", icon:"jlp-192.png", badge:"jlp-192.png", tag:"cam", renotify:true, data:{ url:d.url || "/#cam" }
  }));
});

self.addEventListener("notificationclick", e => {
  e.notification.close();
  const url = new URL((e.notification.data || {}).url || "/#cam", self.location.origin).href;
  e.waitUntil(self.clients.matchAll({ type:"window", includeUncontrolled:true }).then(cs => {
    for (const c of cs){
      if ("focus" in c){ if (c.navigate) c.navigate(url).catch(() => {}); return c.focus(); }
    }
    return self.clients.openWindow(url);
  }));
});
