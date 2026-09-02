# 🚀 Guia Rápido: PWA + APK - Começar Agora!

## ⚡ Tl;dr (Comece em 2 minutos)

### 1️⃣ Instalar dependências Python:
```bash
cd /workspaces/Gestao-usuarios
pip install -r requirements.txt
```

### 2️⃣ Executar o servidor:
```bash
python main.py
```

### 3️⃣ Acessar no navegador:
- **PC**: http://localhost:5000
- **Celular**: http://<seu-ip>:5000
  - (substitua `<seu-ip>` pelo IP real do seu PC)

### 4️⃣ Testar offline:
- Clique em "🔄 Sincronizar" (canto superior direito)
- Ative modo offline (F12 > Network > Offline)
- App continua funcionando! ✅

---

## 📱 Próximos Passos

### Para testar no celular:
```bash
# Descobrir seu IP
ipconfig  # Windows
ifconfig  # Mac/Linux

# Acesse no celular:
http://<seu-ip>:5000
```

### Para gerar APK (depois):
1. Instale Node.js (nodejs.org)
2. Execute:
   ```bash
   npm install
   npx cap add android
   npx cap open android
   ```
3. Em Android Studio: Build > Build APK

---

## 📚 Documentação Completa

Veja: [GUIA_PWA_APK.md](GUIA_PWA_APK.md)

---

## 🛠️ O que foi implementado?

✅ **PWA (Progressive Web App)**
- Funciona offline completamente
- Service Worker com cache automático
- Instalável na tela inicial

✅ **Sincronização de Dados**
- IndexedDB para dados locais
- Botão "🔄 Sincronizar" manual
- Fila de sincronização automática

✅ **API de Dados**
- `/api/clientes-json` - Clientes
- `/api/torneios-json` - Torneios
- `/api/participantes-json` - Participantes
- `/api/confrontos-json` - Confrontos
- `/api/sync` - Sincronização

✅ **Status Online/Offline**
- Indicador visual (🟢 Online / 🔴 Offline)
- Notificações de sincronização

✅ **Pronto para APK**
- Capacitor config incluído
- Package.json pronto

---

## ✨ Recursos Principais

| Recurso | Status | Detalhes |
|---------|--------|----------|
| PWA instalável | ✅ | Funciona no celular como app |
| Offline completo | ✅ | Tudo funciona sem internet |
| Sincronização | ✅ | Manual e automática |
| APK Android | ⏳ | Pronto para gerar (veja guia) |
| HTTPS/Deploy | ⏳ | Heroku/Railway (veja guia) |

---

**Happy coding! 🎉**
