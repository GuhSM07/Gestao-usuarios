# ═══════════════════════════════════════════════════════════════════════════════
# CONEXÃO COM O BANCO DE DADOS
# ═══════════════════════════════════════════════════════════════════════════════
# Este arquivo configura a conexão com o SQLite

import datetime  # Não utilizado, mas deixado para possíveis expansões
from peewee import SqliteDatabase  # ORM Peewee para SQLite

# ─────────────────────────────────────────────────────────────────────────────────
# CRIAR INSTÂNCIA DO BANCO DE DADOS
# ─────────────────────────────────────────────────────────────────────────────────
# SqliteDatabase('customermanager.db') = cria/conecta ao arquivo de banco de dados
# 
# Localização do arquivo: /workspaces/Gestao-usuarios/customermanager.db
# Se o arquivo não existir, Peewee cria automaticamente
# SQLite = banco de dados leve, baseado em arquivo (não precisa de servidor)

db = SqliteDatabase('customermanager.db')

# Este objeto 'db' é importado por:
#   - database/models/torneio.py (cria as tabelas)
#   - configuration.py (conecta e cria tabelas)
#   - routes/torneio.py (acessa os dados)

