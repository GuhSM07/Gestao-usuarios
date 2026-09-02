# 🌐 Deploy na Internet (Heroku/Railway)

## ✅ Pré-requisitos

- Conta Git (GitHub)
- Código na branch `main`
- `Procfile` criado
- `requirements.txt` atualizado

---

## 📦 Etapa 1: Preparar o Código

### Adicionar Gunicorn ao requirements.txt:
```bash
pip install gunicorn python-dotenv
pip freeze > requirements.txt
```

### Criar arquivo `Procfile` (na raiz do projeto):
```
web: gunicorn main:app
```

### Criar `.gitignore`:
```
__pycache__/
*.pyc
*.db
.env
node_modules/
venv/
```

### Fazer commit:
```bash
git add .
git commit -m "Preparado para deploy: PWA + Offline"
git push origin main
```

---

## 🚀 OPÇÃO A: Deploy no Heroku (Gratuito)

### 1. Criar conta em https://www.heroku.com

### 2. Instalar Heroku CLI:
- Windows/Mac: Download em https://devcenter.heroku.com/articles/heroku-cli
- Linux: `curl https://cli-assets.heroku.com/install.sh | sh`

### 3. Fazer login:
```bash
heroku login
```

### 4. Criar app:
```bash
heroku create seu-app-torneios
```

### 5. Deploy:
```bash
git push heroku main
```

### 6. Verificar logs:
```bash
heroku logs --tail
```

### 7. Acessar:
```
https://seu-app-torneios.herokuapp.com
```

---

## 🚀 OPÇÃO B: Deploy no Railway (Recomendado 🌟)

Railway é mais moderno e tem melhor suporte a Python.

### 1. Criar conta em https://railway.app

### 2. Conectar GitHub:
- Clique em "New Project"
- Selecione "Deploy from GitHub repo"
- Autorize Railway no GitHub

### 3. Selecionar repositório:
- Escolha `Gestao-usuarios`

### 4. Configurar:
- Environment: Python
- Root directory: `/` (padrão)

### 5. Deploy automático:
- Railway faz deploy automaticamente ao fazer push!
- Veja progresso em Railway Dashboard

### 6. Configurar variáveis:
```bash
# Em Railway Dashboard > Variables:
DATABASE_URL=sqlite:///database.db
FLASK_ENV=production
```

### 7. Acessar:
```
https://seu-projeto.up.railway.app
```

---

## 🔧 Configuração para Produção

### Desabilitar debug:
```python
# main.py
import os

DEBUG = os.getenv('FLASK_ENV') != 'production'
app.run(debug=DEBUG, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
```

### Variáveis de ambiente (production):
```bash
# .env (local testing)
FLASK_ENV=production
DATABASE_URL=postgresql://user:pass@host/db
SECRET_KEY=seu-secret-key-super-seguro

# Em Heroku/Railway: Configure no dashboard
```

---

## 🔒 Ativar HTTPS (Automático)

- Heroku: Automático com `.herokuapp.com`
- Railway: Automático com `.railway.app`
- Domínio customizado: Configure DNS

---

## 📊 Monitorar em Produção

### Heroku:
```bash
heroku logs --tail
heroku ps:scale web=1
heroku config  # Ver variáveis
```

### Railway:
- Dashboard → Logs
- Dashboard → Deployments
- Dashboard → Metrics

---

## 🚨 Troubleshooting

### App não inicia:
```bash
# Heroku
heroku logs --tail  # Veja o erro

# Railway
# Veja em: Dashboard > Deployments > Logs
```

### Erro 502 Bad Gateway:
- Aumentar dyno (Heroku)
- Aumentar RAM (Railway)

### Banco de dados não conecta:
- Configurar `DATABASE_URL` corretamente
- Se for PostgreSQL, instale: `psycopg2-binary`

---

## 💰 Custos

| Plataforma | Tier Gratuito | Pago |
|-----------|-------------|------|
| Heroku | Deactivated (era $7/mês) | $7-50/mês |
| Railway | $5 créditos/mês | Pague conforme usa |
| DigitalOcean | Não | $4-6/mês |
| AWS | Free tier (1 ano) | Variável |

Railway é melhor custo-benefício em 2024.

---

## ✨ Depois do Deploy

1. **Testar HTTPS**:
   - Vá até https://seu-app.railway.app
   - Clique em "🔄 Sincronizar"
   - Funciona? ✅

2. **Domínio customizado** (opcional):
   - Compre domínio (GoDaddy, Namecheap, etc)
   - Configure DNS em Railway/Heroku
   - Ative HTTPS automático

3. **Publicar APK**:
   - Google Play Store (pago, $25)
   - APK direct install (gratuito)

---

## 📱 Como acessar do APK

Depois de gerar o APK, configure a URL do servidor:

```javascript
// Em seu APK (Capacitor)
const API_URL = 'https://seu-app.railway.app';
```

---

**Pronto! Sua app está na internet! 🎉**
