const publicVapidKey = "BHNBrH6Y9DItzbQg28WFbO6595ZUu8H0e7N7ozN_Q8L6sBG1Y6OBidhUXqxB8hfnFMcAu-EVPyRyxOtPYQbn8EM";

function urlBase64ToUint8Array(base64String) {
    const padding = '='.repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/\-/g, '+').replace(/_/g, '/');
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
}

/** PushManager.subscribe() requires registration.active; register() often resolves earlier. */
function waitForServiceWorkerActive(registration, timeoutMs) {
    if (registration.active) {
        return Promise.resolve(registration);
    }
    const timeout = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Service Worker не активировался за отведённое время')), timeoutMs || 20000);
    });
    const activated = new Promise((resolve, reject) => {
        const worker = registration.installing || registration.waiting;
        if (!worker) {
            navigator.serviceWorker.ready
                .then(() => {
                    if (registration.active) resolve(registration);
                    else reject(new Error('Нет активного Service Worker'));
                })
                .catch(reject);
            return;
        }
        if (worker.state === 'activated') {
            resolve(registration);
            return;
        }
        worker.addEventListener('statechange', () => {
            if (worker.state === 'activated' && registration.active) {
                resolve(registration);
            }
        });
    });
    return Promise.race([activated, timeout]);
}

window.enableNotifications = async function(token, apiBaseUrl, swScriptUrl) {
    if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
        console.error('Push-уведомления не поддерживаются');
        alert('Ваш браузер не поддерживает Push-уведомления');
        return;
    }
    try {
        const swUrl = swScriptUrl || '/app/static/sw.js';
        console.log('Регистрируем Service Worker:', swUrl);
        const registration = await navigator.serviceWorker.register(swUrl);
        console.log('Service Worker зарегистрирован', registration);
        await waitForServiceWorkerActive(registration, 20000);
        console.log('Service Worker активен', registration.active);

        console.log('Проверяем существующую подписку...');
        let subscription = await registration.pushManager.getSubscription();
        if (!subscription) {
            console.log('Подписки нет, создаём новую...');
            const applicationServerKey = urlBase64ToUint8Array(publicVapidKey);
            subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: applicationServerKey
            });
            console.log('Новая подписка создана', subscription);
        } else {
            console.log('Уже есть подписка', subscription);
        }

        const base = (apiBaseUrl || '').replace(/\/$/, '');
        if (!base) {
            alert('Не задан адрес API для подписки на push.');
            return;
        }
        console.log('Отправляем подписку на сервер...');
        const response = await fetch(base + '/api/push-subscribe', {
            method: 'POST',
            body: JSON.stringify(subscription),
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + token
            }
        });
        console.log('Ответ сервера:', response.status);
        if (response.ok) {
            alert('Push-уведомления включены!');
        } else {
            alert('Ошибка сохранения подписки: ' + response.status);
        }
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка: ' + error.message);
    }
};