// Firebase Service Worker for Trivanta Edge ERP
// Handles push notifications and offline functionality

importScripts('https://www.gstatic.com/firebasejs/12.2.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/12.2.1/firebase-messaging-compat.js');

// Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyBwceYbtCryrZcTYvK38GtUNjEnvTVfqXQ",
  authDomain: "trivanta-erp.firebaseapp.com",
  projectId: "trivanta-erp",
  storageBucket: "trivanta-erp.firebasestorage.app",
  messagingSenderId: "1086746404611",
  appId: "1:1086746404611:web:f1b58ca02ab6496cc46b36",
  measurementId: "G-7NG8G150T9"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);

// Initialize Firebase Cloud Messaging
const messaging = firebase.messaging();

// Handle background messages
messaging.onBackgroundMessage((payload) => {
  console.log('Received background message:', payload);

  const notificationTitle = payload.notification.title || 'Trivanta ERP';
  const notificationOptions = {
    body: payload.notification.body || 'You have a new notification',
    icon: '/static/images/logo.png',
    badge: '/static/images/badge.png',
    data: payload.data
  };

  return self.registration.showNotification(notificationTitle, notificationOptions);
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  console.log('Notification clicked:', event);

  event.notification.close();

  if (event.notification.data && event.notification.data.url) {
    event.waitUntil(
      clients.openWindow(event.notification.data.url)
    );
  }
});

// Handle push events
self.addEventListener('push', (event) => {
  console.log('Push event received:', event);

  if (event.data) {
    const data = event.data.json();
    const notificationTitle = data.title || 'Trivanta ERP';
    const notificationOptions = {
      body: data.body || 'You have a new notification',
      icon: '/static/images/logo.png',
      badge: '/static/images/badge.png',
      data: data
    };

    event.waitUntil(
      self.registration.showNotification(notificationTitle, notificationOptions)
    );
  }
});

// Handle install event
self.addEventListener('install', (event) => {
  console.log('Service Worker installed');
  self.skipWaiting();
});

// Handle activate event
self.addEventListener('activate', (event) => {
  console.log('Service Worker activated');
  event.waitUntil(self.clients.claim());
});

// Handle fetch events for offline support
self.addEventListener('fetch', (event) => {
  if (event.request.url.includes('/api/')) {
    // Handle API requests
    event.respondWith(
      fetch(event.request)
        .catch(() => {
          // Return offline response for API requests
          return new Response(
            JSON.stringify({ error: 'Offline mode - please check your connection' }),
            { 
              status: 503,
              headers: { 'Content-Type': 'application/json' }
            }
          );
        })
    );
  }
});
