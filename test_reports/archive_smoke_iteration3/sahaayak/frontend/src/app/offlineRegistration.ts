export function registerOfflineShell() {
 if (!('serviceWorker' in navigator)) return;
 navigator.serviceWorker.register('/sw.js').then(async () => {
   const ready = await navigator.serviceWorker.ready;
   const urls = performance.getEntriesByType('resource').map(entry => entry.name).filter(url => new URL(url).origin === location.origin && /\.(js|css|jpg|png|woff2)(\?|$)/.test(url));
   ready.active?.postMessage({type:'CACHE_APP',urls});
 }).catch(() => { /* IndexedDB queue remains usable when shell caching is unavailable. */ });
}