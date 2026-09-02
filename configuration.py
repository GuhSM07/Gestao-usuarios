# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO CENTRAL DA APLICAÇÃO
# ═══════════════════════════════════════════════════════════════════════════════
# Este arquivo centraliza a configuração da aplicação Flask:
# - Registra as rotas (blueprints)
# - Inicializa o banco de dados
# - Cria as tabelas

# IMPORTAÇÕES: Rotas (blueprints)
from routes.home import home_route  # Rota inicial/home
from routes.cliente import cliente_route  # Rotas de gestão de clientes
from routes.torneio import torneio_route  # Rotas de gestão de torneios
from routes.api import api_route  # Rotas de API (sincronização offline)

# IMPORTAÇÕES: Banco de dados
from database.database import db  # Conexão com banco (SQLite)
from database.models.cliente import Cliente  # Modelo/tabela Cliente
from database.models.torneio import Torneio, Participante, Confronto  # Modelos/tabelas do Torneio


# ─────────────────────────────────────────────────────────────────────────────────
# FUNÇÃO PRINCIPAL: configure_all()
# ─────────────────────────────────────────────────────────────────────────────────
# O que faz: Função de entrada que configura TUDO de uma vez
# Chamada por: main.py -> configure_all(app)

def configure_all(app):
    """Configura toda a aplicação de uma vez"""
    # Registra as rotas (URLs)
    configure_routes(app)
    # Inicializa o banco de dados
    configure_db()


# ─────────────────────────────────────────────────────────────────────────────────
# FUNÇÃO: configure_routes()
# ─────────────────────────────────────────────────────────────────────────────────
# O que faz: Registra as rotas (blueprints) na aplicação Flask
# Blueprints: Forma de organizar rotas em módulos separados

def configure_routes(app):
    """Registra todos os blueprints (módulos de rotas) na aplicação"""
    
    # Registra a rota de HOME (sem url_prefix, portanto começa em /)
    # URL base: /
    app.register_blueprint(home_route)
    
    # Registra a rota de CLIENTES com prefixo
    # URL base: /clientes
    # Exemplo: GET /clientes/ (listar)
    app.register_blueprint(cliente_route, url_prefix='/clientes')
    
    # Registra a rota de TORNEIOS com prefixo
    # URL base: /torneios
    # Exemplo: GET /torneios/ (listar)
    #          POST /torneios/novo (criar)
    #          GET /torneios/<id> (detalhes)
    app.register_blueprint(torneio_route, url_prefix='/torneios')
    
    # Registra a rota de API (para sincronização offline)
    # URL base: /api
    # Exemplo: GET /api/clientes-json (dados para cache)
    #          POST /api/sync (sincronização)
    app.register_blueprint(api_route)


# ─────────────────────────────────────────────────────────────────────────────────
# FUNÇÃO: configure_db()
# ─────────────────────────────────────────────────────────────────────────────────
# O que faz: 
#   1. Conecta ao banco de dados SQLite
#   2. Cria as tabelas (se não existirem)

def configure_db():
    """Configura e inicializa o banco de dados"""
    
    # Conecta ao banco de dados
    # Se o arquivo não existir, Peewee cria automaticamente
    # Arquivo: customermanager.db (localizado em /workspaces/Gestao-usuarios/)
    db.connect()
    
    # Cria as tabelas se não existirem
    # A ordem importa: Cliente é independente
    # Participante e Confronto dependem de Torneio
    db.create_tables([Cliente, Torneio, Participante, Confronto])

