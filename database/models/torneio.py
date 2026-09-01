# ═══════════════════════════════════════════════════════════════════════════════
# MODELOS DO BANCO DE DADOS - TABELAS DO SISTEMA DE TORNEIOS
# ═══════════════════════════════════════════════════════════════════════════════
# Este arquivo define as 3 tabelas principais:
# 1. Torneio - Informações do torneio
# 2. Participante - Pessoas que participam
# 3. Confronto - Matches/confrontos entre participantes
#
# ORM: Peewee (Object-Relational Mapping)
# DB: SQLite (arquivo customermanager.db)

from peewee import Model, DateTimeField, CharField, ForeignKeyField, IntegerField
from database.database import db
from database.models.cliente import Cliente
import datetime


# ─────────────────────────────────────────────────────────────────────────────────
# TABELA 1: TORNEIO
# ─────────────────────────────────────────────────────────────────────────────────
# O que armazena: Informações do torneio
# Colunas:
#   - id: PRIMARY KEY (auto-incremento)
#   - nome: Nome do torneio (texto)
#   - status: Estado atual ('em_progresso' ou 'concluido')
#   - data_criacao: Data e hora de criação (automática)

class Torneio(Model):
    """Tabela que armazena os torneios"""
    # CharField = texto curto
    nome = CharField()
    
    # DateTimeField = data e hora
    # default=datetime.datetime.now = automaticamente preenche com data/hora atual
    data_criacao = DateTimeField(default=datetime.datetime.now)
    
    # CharField com valor padrão
    # 'em_progresso' = torneio ainda está acontecendo
    # 'concluido' = torneio terminou, campeão foi escolhido
    status = CharField(default='em_progresso')
    
    # Meta: Define qual banco de dados usar
    class Meta:
        database = db  # Usa a conexão db configurada em database.py


# ─────────────────────────────────────────────────────────────────────────────────
# TABELA 2: PARTICIPANTE
# ─────────────────────────────────────────────────────────────────────────────────
# O que armazena: Pessoas que participam de um torneio
# Colunas:
#   - id: PRIMARY KEY (auto-incremento)
#   - nome: Nome do participante
#   - torneio: FOREIGN KEY para Torneio (relacionamento)
#   - data_registro: Data e hora de inscrição
#
# Relacionamento: MUITOS Participantes para UM Torneio
# Um torneio pode ter vários participantes
# Um participante pertence a apenas um torneio

class Participante(Model):
    """Tabela que armazena os participantes de cada torneio"""
    
    # ForeignKeyField = RELACIONAMENTO com Cliente
    # Um participante é vinculado a um cliente já registrado
    # backref='participacoes' = permite acessar participações via cliente.participacoes
    cliente = ForeignKeyField(Cliente, backref='participacoes')
    
    # ForeignKeyField = RELACIONAMENTO com outra tabela
    # Participante.torneio_id referencia a chave primária de Torneio
    # backref='participantes' = permite acessar participantes via torneio.participantes
    torneio = ForeignKeyField(Torneio, backref='participantes')
    
    # Data e hora de quando o participante foi adicionado ao torneio
    data_inscricao = DateTimeField(default=datetime.datetime.now)
    
    # Meta: Define qual banco de dados usar
    class Meta:
        database = db


# ─────────────────────────────────────────────────────────────────────────────────
# TABELA 3: CONFRONTO
# ─────────────────────────────────────────────────────────────────────────────────
# O que armazena: Cada confronto (match) do torneio
# Colunas:
#   - id: PRIMARY KEY (auto-incremento)
#   - torneio: FOREIGN KEY para Torneio
#   - participante1: FOREIGN KEY para Participante (player 1)
#   - participante2: FOREIGN KEY para Participante (player 2, pode ser NULL)
#   - vencedor: FOREIGN KEY para Participante (pode ser NULL)
#   - round: Número do round/fase (1, 2, 3...)
#   - data_confronto: Data e hora do confronto
#
# Relacionamentos:
#   - Cada confronto pertence a UM torneio
#   - Cada confronto tem ATÉ 2 participantes
#   - Cada confronto pode ter 0 ou 1 vencedor

class Confronto(Model):
    """Tabela que armazena cada confronto/match do torneio"""
    
    # Qual torneio este confronto pertence
    # backref='confrontos' = permite acessar confrontos via torneio.confrontos
    torneio = ForeignKeyField(Torneio, backref='confrontos')
    
    # Primeiro participante do confronto
    # null=True = pode ser vazio (para byes)
    # backref='confrontos_como_p1' = rastreia confrontos em que este é p1
    participante1 = ForeignKeyField(
        Participante, 
        backref='confrontos_como_p1', 
        null=True
    )
    
    # Segundo participante do confronto
    # null=True = pode ser vazio (bye = vitória automática)
    # backref='confrontos_como_p2' = rastreia confrontos em que este é p2
    participante2 = ForeignKeyField(
        Participante, 
        backref='confrontos_como_p2', 
        null=True
    )
    
    # Quem venceu este confronto
    # null=True = confronto ainda não foi decidido
    # backref='confrontos_vencidos' = rastreia confrontos que este participante venceu
    vencedor = ForeignKeyField(
        Participante, 
        backref='confrontos_vencidos', 
        null=True
    )
    
    # IntegerField = número inteiro
    # Qual fase do torneio (1 = primeira, 2 = semifinal, 3 = final, etc)
    # Usado para organizar e exibir confrontos por fase
    round = IntegerField()
    
    # Data e hora em que o confronto foi criado
    data_confronto = DateTimeField(default=datetime.datetime.now)
    
    # Meta: Define qual banco de dados usar
    class Meta:
        database = db

