// Service Worker para PWA - Funciona offline, cache automático
const CACHE_VERSION = 'torneios-v1';
const DYNAMIC_CACHE = 'dynamic-v1';
const API_CACHE = 'api-cache-v1';

// Arquivos essenciais para cache no install
const ESSENTIAL_FILES = [
  '/',
  '/static/css/app.css',
  '/static/js/cru.js',
  '/offline-fallback'
];

// Instalação do Service Worker - Cache dos arquivos estáticos
self.addEventListener('install', (event) => {
  console.log('Service Worker installing...');
  
  event.waitUntil(
    caches.open(CACHE_VERSION).then((cache) => {
      console.log('Caching essential files');
      return cache.addAll(ESSENTIAL_FILES).catch(() => {
        // Se falhar, continua mesmo assim (pode estar offline)
        console.log('Failed to cache some essential files, but continuing');
      });
    })
  );
  
  // Força o novo Service Worker a ativar imediatamente
  self.skipWaiting();
});

// Ativação - Remove caches antigos
self.addEventListener('activate', (event) => {
  console.log('Service Worker activating...');
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((cacheName) => {
            return (
              cacheName !== CACHE_VERSION &&
              cacheName !== DYNAMIC_CACHE &&
              cacheName !== API_CACHE
            );
          })
          .map((cacheName) => {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          })
      );
    })
  );
  
  self.clients.claim();
});

// Estratégia de fetch - Network first, fallback cache
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Ignora requisições para domínios externos e websockets
  if (url.origin !== location.origin) {
    return;
  }

  // Tratamento especial para API de sincronização
  if (request.url.includes('/api/sync')) {
    event.respondWith(handleApiSync(request));
    return;
  }

  // Para requisições de navegação (HTML pages)
  if (request.mode === 'navigate') {
    event.respondWith(handleNavigation(request));
    return;
  }

  // Para CSS, JS, imagens (cache first)
  if (
    request.url.includes('/static/') ||
    request.url.endsWith('.css') ||
    request.url.endsWith('.js') ||
    request.url.endsWith('.png') ||
    request.url.endsWith('.jpg') ||
    request.url.endsWith('.gif') ||
    request.url.endsWith('.svg')
  ) {
    event.respondWith(handleStatic(request));
    return;
  }

  // Para outras requisições (network first)
  event.respondWith(handleNetwork(request));
});

// Navegação: tenta network, fallback para cache
async function handleNavigation(request) {
  try {
    const response = await fetch(request);
    
    // Cache a resposta se for sucesso
    if (response.ok) {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    // Offline: retorna do cache
    const cached = await caches.match(request);
    if (cached) {
      return cached;
    }
    
    // Se não tem cache, retorna página offline
    return caches.match('/offline-fallback').catch(() => {
      return new Response('Offline - página não encontrada no cache', {
        status: 503,
        statusText: 'Service Unavailable',
        headers: new Headers({
          'Content-Type': 'text/plain'
        })
      });
    });
  }
}

// Arquivos estáticos: cache first, network fallback
async function handleStatic(request) {
  const cached = await caches.match(request);
  if (cached) {
    return cached;
  }

  try {
    const response = await fetch(request);
    
    if (response.ok) {
      const cache = await caches.open(CACHE_VERSION);
      cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    return new Response('Arquivo não encontrado', {
      status: 404,
      statusText: 'Not Found'
    });
  }
}

// Requisições de rede: tenta network, fallback cache
async function handleNetwork(request) {
  try {
    const response = await fetch(request);
    
    // Cache a resposta se for sucesso
    if (response.ok && request.method === 'GET') {
      const cache = await caches.open(DYNAMIC_CACHE);
      cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    // Offline: retorna do cache se existir
    const cached = await caches.match(request);
    return cached || new Response('Offline - recurso não disponível', {
      status: 503,
      statusText: 'Service Unavailable'
    });
  }
}

// API de sincronização: sempre tenta network
async function handleApiSync(request) {
  try {
    const response = await fetch(request);
    return response;
  } catch (error) {
    // Se falhar a sincronização, retorna erro
    return new Response(
      JSON.stringify({ error: 'Sincronização falhou - sem conexão' }),
      {
        status: 503,
        statusText: 'Service Unavailable',
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }
}

// Mensagens do cliente para o service worker
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'CLEAR_CACHE') {
    caches.delete(DYNAMIC_CACHE);
  }
});
