self.addEventListener('install', event => {
    console.log('[SW] Install');
    self.skipWaiting(); // заставляет SW активироваться сразу
});

self.addEventListener('activate', event => {
    console.log('[SW] Activate');
    event.waitUntil(clients.claim()); // захватывает все клиенты
});

self.addEventListener('push', event => {
    console.log('[SW] Push received', event);
    let data = { title: 'Уведомление', body: 'Тест' };
    if (event.data) {
        try { data = event.data.json(); } catch(e) { data.body = event.data.text(); }
    }
    event.waitUntil(
        self.registration.showNotification(data.title, {
            body: data.body,
            icon: '/icon.png',
            vibrate: [200, 100, 200]
        })
    );
});

self.addEventListener('notificationclick', event => {
    event.notification.close();
    event.waitUntil(clients.openWindow('/'));
});