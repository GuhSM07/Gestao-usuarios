# 📱 Guia: PWA + APK - De Web para Mobile

## 🎯 Visão Geral

Sua aplicação foi transformada em uma **Progressive Web App (PWA)** que:
- ✅ Funciona **100% offline** no celular e PC
- ✅ Funciona **online** também (web completa)
- ✅ Sincroniza dados com botão manual
- ✅ Pode virar um **APK** nativo

---

## 📝 Resumo das Mudanças Implementadas

### 1. **Service Worker** (`static/js/service-worker.js`)
- Cache automático de arquivos estáticos
- Funciona completamente offline
- Estratégia: Network-first para HTML, Cache-first para CSS/JS

### 2. **Progressive Web App** (`static/manifest.json`)
- Define como a app aparece no celular
- Ícone, nome, cor da barra
- Instalável na tela inicial

### 3. **Sincronização Offline** (`static/js/offline-sync.js`)
- IndexedDB para armazenar dados localmente
- Fila de sincronização automática
- Botão de sincronização manual

### 4. **API de Sincronização** (`routes/api.py`)
- `/api/clientes-json` - Carrega clientes
- `/api/torneios-json` - Carrega torneios
- `/api/participantes-json` - Carrega participantes
- `/api/confrontos-json` - Carrega confrontos
- `/api/sync` - Sincroniza dados

### 5. **Atualizações Flask**
- Adicionado CORS para requisições cruzadas
- Servidor aceita conexões de qualquer IP (não apenas localhost)
- Novas rotas de API registradas

---

## 🚀 ETAPA 1: Executar Localmente (Teste)

### Instalar dependências:
```bash
cd /workspaces/Gestao-usuarios
pip install -r requirements.txt
```

### Executar o servidor:
```bash
python main.py
```

### Acessar no navegador:
- **PC/Laptop**: http://localhost:5000
- **Celular na rede**: http://<seu-ip-do-pc>:5000
  - Para encontrar seu IP: `ipconfig` (Windows) ou `ifconfig` (Linux/Mac)

### Testar offline:
1. Abra a app no navegador
2. Clique no botão "🔄 Sincronizar" para carregar dados
3. Ative o modo offline (F12 > Network > Offline)
4. A app continua funcionando! ✅

---

## 🌐 ETAPA 2: Publicar na Internet (Servidor)

### Opção A: Heroku (Gratuito + fácil)

#### 1. Criar conta em heroku.com
#### 2. Instalar Heroku CLI
#### 3. Fazer login:
```bash
heroku login
```

#### 4. Criar arquivo `Procfile` na raiz do projeto:
```
web: gunicorn main:app
```

#### 5. Instalar gunicorn:
```bash
pip install gunicorn
pip freeze > requirements.txt
```

#### 6. Criar app Heroku:
```bash
heroku create seu-app-nome
```

#### 7. Deploy:
```bash
git add .
git commit -m "PWA + Offline Ready"
git push heroku main
```

#### 8. Acessar:
```
https://seu-app-nome.herokuapp.com
```

---

### Opção B: Railway (Mais moderno)

#### 1. Criar conta em railway.app
#### 2. Conectar seu GitHub
#### 3. Criar novo projeto a partir do repositório
#### 4. Configurar variáveis de ambiente (se necessário)
#### 5. Deploy automático!

---

### Opção C: AWS/DigitalOcean (Mais poderoso)

Fora do escopo deste guia, mas muito documentado online.

---

## 📲 ETAPA 3: Transformar em APK

### Opção A: Capacitor (Recomendado 🌟)

#### 1. Instalar Node.js se não tiver:
```bash
# macOS
brew install node

# Windows: Download em nodejs.org
# Linux: apt-get install nodejs npm
```

#### 2. Instalar Capacitor globalmente:
```bash
npm install -g @capacitor/cli
```

#### 3. Inicializar Capacitor no seu projeto:
```bash
cd /workspaces/Gestao-usuarios
npm init -y
npm install @capacitor/core @capacitor/cli @capacitor/android @capacitor/ios
```

#### 4. Criar arquivo `capacitor.config.json` na raiz:
```json
{
  "appId": "com.example.torneios",
  "appName": "Torneios",
  "webDir": ".",
  "server": {
    "androidScheme": "https"
  },
  "plugins": {
    "SplashScreen": {
      "launchShowDuration": 0
    }
  }
}
```

#### 5. Adicionar plataforma Android:
```bash
npx cap add android
```

#### 6. Abrir Android Studio:
```bash
npx cap open android
```

#### 7. Em Android Studio:
- Build > Build Bundle(s)/APK(s) > Build APK(s)
- Aguarde...
- APK pronto em: `android/app/release/app-release.apk`

#### 8. Instalar no celular:
```bash
npx cap run android
```

---

### Opção B: Cordova (Alternativa)

#### 1. Instalar Cordova:
```bash
npm install -g cordova
```

#### 2. Criar projeto:
```bash
cordova create torneios-app
cd torneios-app
```

#### 3. Adicionar plataforma Android:
```bash
cordova platform add android
```

#### 4. Copiar arquivos da web (`static/` e `templates/`)
```bash
cp -r /workspaces/Gestao-usuarios/static www/
cp -r /workspaces/Gestao-usuarios/templates www/
```

#### 5. Build:
```bash
cordova build android --release
```

#### 6. APK em: `platforms/android/release/android-release.apk`

---

### Opção C: Flutter/React Native (Mais trabalho)

Se quiser um app **verdadeiramente nativo** (melhor performance), considere:
- **Flutter**: Use `flutter_web_view` + plugin de IPC
- **React Native**: Migre para React Native + `react-native-webview`

Mas isso é uma reescrita completa.

---

## 🔧 Configuração para Sincronização

### No celular/PC, quando usa a PWA:

1. **Primeira vez (offline)**:
   - App começa vazio
   - Nenhum dado disponível ainda

2. **Conectar à internet**:
   - Clique no botão "🔄 Sincronizar"
   - Dados do servidor são baixados para IndexedDB
   - Mensagem de sucesso aparece

3. **Ficar offline**:
   - App continua funcionando com dados em cache
   - Pode modificar dados localmente

4. **Reconectar**:
   - Clique "🔄 Sincronizar" novamente
   - Mudanças locais são enviadas para o servidor
   - Dados do servidor são recarregados

---

## 📊 Arquitetura de Dados

```
┌─────────────────────────────────────────┐
│     Navegador (PWA)                     │
├─────────────────────────────────────────┤
│  ┌─────────────────────────────────┐   │
│  │  Service Worker (Cache)         │   │
│  │  - Funciona offline             │   │
│  │  - Cache automático de arquivos │   │
│  └─────────────────────────────────┘   │
│  ┌─────────────────────────────────┐   │
│  │  IndexedDB (Dados Locais)       │   │
│  │  - Clientes                     │   │
│  │  - Torneios                     │   │
│  │  - Participantes                │   │
│  │  - Confrontos                   │   │
│  │  - Fila de sincronização        │   │
│  └─────────────────────────────────┘   │
└──────────────┬──────────────────────────┘
               │ HTTP/HTTPS (quando online)
               ↓
       ┌──────────────────┐
       │  Flask Server    │
       │  - /api/* routes │
       │  - SQLite DB     │
       └──────────────────┘
```

---

## 🔐 Segurança para Produção

### Antes de fazer deploy em produção:

#### 1. **Desabilitar debug**:
```python
# main.py
app.run(debug=False, host='0.0.0.0', port=5000)
```

#### 2. **Usar HTTPS** (obrigatório):
- Heroku/Railway fazem isso automaticamente
- Se usar servidor próprio: Instale certificado SSL (Let's Encrypt é gratuito)

#### 3. **Variáveis de ambiente**:
```python
import os
DATABASE_URL = os.getenv('DATABASE_URL', 'database.db')
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
```

#### 4. **Adicionar autenticação** (opcional):
- Flask-Login para login de usuários
- JWT tokens para API

---

## 📞 Troubleshooting

### Service Worker não funciona
```bash
# Limpar cache no navegador
F12 > Application > Clear storage > Clear site data
```

### Dados não sincronizam
```javascript
// No console do navegador
offlineSync.syncWithServer();  // Sincroniza manualmente
offlineSync.showSyncNotification('Teste');  // Testa notificação
```

### APK não conecta ao servidor
- Verifique se servidor está rodando em `0.0.0.0:5000`
- Verifique IP do PC (execute `ipconfig` ou `ifconfig`)
- Teste conexão: `http://<ip>:5000/torneios/`
- No APK, configure URL do servidor corretamente

### Firebase como alternativa (para APK)
Se quiser algo mais profissional e fácil:
- Google Firebase (banco + autenticação + hosting)
- AWS Amplify
- Supabase (PostgreSQL + Auth)

---

## 📚 Próximos Passos

1. **Testar offline** ✅ (implementado)
2. **Deploy em servidor** (escolha opção A/B/C acima)
3. **Gerar APK** (escolha Capacitor/Cordova acima)
4. **Adicionar autenticação** (user login)
5. **Melhorar UX/UI** (animações, temas)
6. **Publicar na Play Store** (pago, $25)

---

## 🎓 Recursos Úteis

- PWA: https://web.dev/progressive-web-apps/
- Service Worker: https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API
- IndexedDB: https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API
- Capacitor: https://capacitorjs.com/
- Heroku: https://www.heroku.com/

---

**Desenvolvido com ❤️ para Torneios Online 🏆**
