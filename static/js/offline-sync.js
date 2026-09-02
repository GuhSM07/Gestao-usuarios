/**
 * offline-sync.js - Sistema de sincronização offline/online
 * Armazena dados em IndexedDB e sincroniza com servidor quando conectado
 */

class OfflineSync {
  constructor() {
    this.db = null;
    this.dbName = 'TorneiosDB';
    this.dbVersion = 1;
    this.stores = {
      clientes: { keyPath: 'id', indexes: [{ name: 'nome', keyPath: 'nome' }] },
      torneios: { keyPath: 'id', indexes: [{ name: 'nome', keyPath: 'nome' }] },
      participantes: { keyPath: 'id', indexes: [{ name: 'torneio_id', keyPath: 'torneio_id' }] },
      confrontos: { keyPath: 'id', indexes: [{ name: 'torneio_id', keyPath: 'torneio_id' }] },
      syncQueue: { keyPath: 'id', autoIncrement: true } // Fila de sincronização
    };
    this.isOnline = navigator.onLine;
    this.syncInProgress = false;
    
    this.init();
  }

  /**
   * Inicializa o IndexedDB e registra listeners de conexão
   */
  async init() {
    try {
      await this.openDatabase();
      this.setupNetworkListeners();
      console.log('✓ OfflineSync inicializado com sucesso');
    } catch (error) {
      console.error('✗ Erro ao inicializar OfflineSync:', error);
    }
  }

  /**
   * Abre ou cria o banco de dados
   */
  openDatabase() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.dbName, this.dbVersion);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve(this.db);
      };

      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        
        // Cria os object stores
        Object.entries(this.stores).forEach(([storeName, config]) => {
          if (!db.objectStoreNames.contains(storeName)) {
            const store = db.createObjectStore(storeName, {
              keyPath: config.keyPath,
              autoIncrement: config.autoIncrement || false
            });
            
            // Cria índices
            if (config.indexes) {
              config.indexes.forEach(idx => {
                store.createIndex(idx.name, idx.keyPath, { unique: false });
              });
            }
          }
        });
      };
    });
  }

  /**
   * Configura listeners para online/offline
   */
  setupNetworkListeners() {
    window.addEventListener('online', () => {
      this.isOnline = true;
      console.log('✓ Voltou online - sincronizando...');
      this.showSyncNotification('Online - Sincronizando dados...');
      this.syncWithServer();
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
      console.log('✗ Ficou offline - usando dados locais');
      this.showSyncNotification('Offline - Usando dados locais', 'warning');
    });
  }

  /**
   * Salva dados localmente (cria/atualiza)
   */
  async saveLocal(storeName, data) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.put(data);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
    });
  }

  /**
   * Carrega dados localmente
   */
  async getLocal(storeName, key) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readonly');
      const store = transaction.objectStore(storeName);
      const request = store.get(key);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
    });
  }

  /**
   * Lista todos os dados de uma store
   */
  async getAllLocal(storeName) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readonly');
      const store = transaction.objectStore(storeName);
      const request = store.getAll();

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
    });
  }

  /**
   * Adiciona operação à fila de sincronização
   */
  async queueSync(action, store, data) {
    const syncItem = {
      timestamp: Date.now(),
      action, // 'create', 'update', 'delete'
      store,
      data,
      synced: false
    };

    return this.saveLocal('syncQueue', syncItem);
  }

  /**
   * Sincroniza dados com o servidor
   */
  async syncWithServer() {
    if (this.syncInProgress || !this.isOnline) {
      return;
    }

    this.syncInProgress = true;

    try {
      // Pega a fila de sincronização
      const queue = await this.getAllLocal('syncQueue');

      if (queue.length === 0) {
        console.log('✓ Sem dados para sincronizar');
        this.showSyncNotification('Sincronização concluída', 'success');
        this.syncInProgress = false;
        return;
      }

      console.log(`Sincronizando ${queue.length} operação(ões)...`);

      // Processa cada item da fila
      for (const item of queue) {
        try {
          const response = await fetch('/api/sync', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(item)
          });

          if (response.ok) {
            // Remove da fila após sucesso
            await this.deleteLocal('syncQueue', item.id);
            console.log(`✓ Sincronizado: ${item.action} em ${item.store}`);
          } else {
            console.error(`✗ Erro ao sincronizar: ${response.status}`);
            throw new Error(`Status ${response.status}`);
          }
        } catch (error) {
          console.error('✗ Erro de sincronização:', error);
          break; // Para na primeira falha
        }
      }

      // Recarrega dados do servidor
      await this.loadServerData();
      this.showSyncNotification('Sincronização concluída com sucesso!', 'success');
    } catch (error) {
      console.error('✗ Erro na sincronização:', error);
      this.showSyncNotification('Erro na sincronização', 'error');
    } finally {
      this.syncInProgress = false;
    }
  }

  /**
   * Carrega dados do servidor para local
   */
  async loadServerData() {
    try {
      // Carrega clientes
      const clientesRes = await fetch('/api/clientes-json');
      const clientes = await clientesRes.json();
      for (const cliente of clientes) {
        await this.saveLocal('clientes', cliente);
      }

      // Carrega torneios
      const torneiosRes = await fetch('/api/torneios-json');
      const torneios = await torneiosRes.json();
      for (const torneio of torneios) {
        await this.saveLocal('torneios', torneio);
      }

      // Carrega participantes
      const participantesRes = await fetch('/api/participantes-json');
      const participantes = await participantesRes.json();
      for (const participante of participantes) {
        await this.saveLocal('participantes', participante);
      }

      // Carrega confrontos
      const confrontosRes = await fetch('/api/confrontos-json');
      const confrontos = await confrontosRes.json();
      for (const confronto of confrontos) {
        await this.saveLocal('confrontos', confronto);
      }

      console.log('✓ Dados do servidor carregados com sucesso');
    } catch (error) {
      console.error('✗ Erro ao carregar dados do servidor:', error);
    }
  }

  /**
   * Deleta dados localmente
   */
  async deleteLocal(storeName, key) {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.delete(key);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve();
    });
  }

  /**
   * Limpa todo o banco local (cuidado!)
   */
  async clearLocal() {
    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction(
        Object.keys(this.stores),
        'readwrite'
      );

      Object.keys(this.stores).forEach(storeName => {
        transaction.objectStore(storeName).clear();
      });

      transaction.onerror = () => reject(transaction.error);
      transaction.oncomplete = () => {
        console.log('✓ Banco local limpo');
        resolve();
      };
    });
  }

  /**
   * Mostra notificação de sincronização
   */
  showSyncNotification(message, type = 'info') {
    // Cria elemento de notificação
    const notification = document.createElement('div');
    notification.className = `sync-notification sync-${type}`;
    notification.innerHTML = `
      <span>${message}</span>
      <button onclick="this.parentElement.remove()" style="margin-left: 10px; cursor: pointer;">✕</button>
    `;
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 12px 16px;
      border-radius: 4px;
      background: ${type === 'success' ? '#27ae60' : type === 'error' ? '#e74c3c' : type === 'warning' ? '#f39c12' : '#3498db'};
      color: white;
      font-weight: bold;
      z-index: 9999;
      box-shadow: 0 2px 8px rgba(0,0,0,0.2);
      animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notification);

    // Remove após 4 segundos
    setTimeout(() => {
      notification.remove();
    }, 4000);
  }
}

// Inicializa o sistema
const offlineSync = new OfflineSync();

// Função para forçar sincronização manual
async function syncNow() {
  if (!offlineSync.isOnline) {
    offlineSync.showSyncNotification('Sem conexão à internet', 'error');
    return;
  }

  offlineSync.showSyncNotification('Sincronizando...', 'info');
  await offlineSync.syncWithServer();
}

// Carrega dados inicialmente se estiver online
if (navigator.onLine) {
  offlineSync.loadServerData();
}
