# ═══════════════════════════════════════════════════════════════════════════════
# ROTAS DO TORNEIO - Gerenciam toda a lógica do sistema de torneio/chaveamento
# ═══════════════════════════════════════════════════════════════════════════════
# Este arquivo contém 9 funções principais que controlam:
# 1. Listar torneios
# 2. Criar novo torneio
# 3. Ver detalhes de um torneio
# 4. Adicionar participante
# 5. Deletar participante
# 6. Gerar bracket aleatório
# 7. Gerar bracket manual
# 8. Registrar vencedor de confronto
# 9. Gerar próximo round automaticamente

from flask import Blueprint, render_template, request, redirect, url_for, jsonify, abort
from database.models.torneio import Torneio, Participante, Confronto
from database.models.cliente import Cliente
from database.database import db
import random

# Cria um Blueprint para organizar rotas relacionadas a torneios
# URL base: /torneios (configurado em configuration.py)
torneio_route = Blueprint('torneio', __name__)

# ─────────────────────────────────────────────────────────────────────────────────
# 1. LISTAR TORNEIOS - Página inicial com todos os torneios
# ─────────────────────────────────────────────────────────────────────────────────
# URL: GET /torneios/
# O que faz: Busca TODOS os torneios do banco e exibe em grid de cards
# Onde fica: templates/listar_torneios.html

@torneio_route.route('/', methods=['GET'])
def listar_torneios():
    """Lista todos os torneios da base de dados em uma página"""
    # Consulta o banco de dados para trazer todos os torneios existentes
    torneios = Torneio.select()
    # Renderiza e retorna o template HTML com a lista de torneios
    return render_template('listar_torneios.html', torneios=torneios)


# ─────────────────────────────────────────────────────────────────────────────────
# 2. CRIAR NOVO TORNEIO - Formulário + criação
# ─────────────────────────────────────────────────────────────────────────────────
# URL: GET /torneios/novo (exibe formulário) | POST /torneios/novo (cria)
# O que faz: 
#   - GET: Exibe formulário para entrada do nome
#   - POST: Recebe nome, cria no BD, redireciona para detalhes do novo torneio
# Onde fica: templates/form_torneio.html (formulário)

@torneio_route.route('/novo', methods=['GET', 'POST'])
def novo_torneio():
    """Criar um novo torneio no banco de dados"""
    # Se o método é POST, significa que o formulário foi enviado
    if request.method == 'POST':
        # Pega o nome do torneio enviado pelo formulário HTML
        nome = request.form.get('nome')
        
        # Pega lista de IDs dos participantes (clientes) selecionados
        participante_ids = request.form.getlist('participantes')
        
        # Valida se o nome foi preenchido e há participantes selecionados
        if nome and participante_ids:
            # INSERT: Cria um novo torneio no banco de dados
            torneio = Torneio.create(nome=nome)
            
            # Adiciona cada cliente selecionado como participante do torneio
            for cliente_id in participante_ids:
                try:
                    cliente = Cliente.get_by_id(cliente_id)
                    Participante.create(cliente=cliente, torneio=torneio)
                except Cliente.DoesNotExist:
                    pass  # Ignora se cliente não existir
            
            # Redireciona para a página de detalhes do torneio recém-criado
            return redirect(url_for('torneio.detalhe_torneio', torneio_id=torneio.id))
    
    # GET: Exibe o formulário de criação de torneio com lista de clientes
    clientes = Cliente.select()
    return render_template('form_torneio.html', clientes=clientes)


# ─────────────────────────────────────────────────────────────────────────────────
# 3. DETALHES DO TORNEIO - Página principal de gerenciamento
# ─────────────────────────────────────────────────────────────────────────────────
# URL: GET /torneios/<id>
# O que faz: 
#   - Exibe a página principal do torneio
#   - Mostra lista de participantes (com add/delete)
#   - Mostra todos os confrontos por fase/round
#   - Permite registrar vencedores
#   - Exibe o campeão quando terminar
# Onde fica: templates/detalhe_torneio.html

@torneio_route.route('/<int:torneio_id>', methods=['GET'])
def detalhe_torneio(torneio_id):
    """Exibe a página principal de um torneio específico"""
    # Tenta buscar o torneio com o ID fornecido
    try:
        torneio = Torneio.get(Torneio.id == torneio_id)
    except Torneio.DoesNotExist:
        # Se não encontrar na BD, retorna erro 404
        abort(404)
    
    # SELECT: Pega lista de participantes do torneio
    participantes = list(torneio.participantes)
    
    # SELECT: Pega todos os confrontos ordenados por round e ID
    confrontos = list(torneio.confrontos.order_by(Confronto.round, Confronto.id))
    
    # Organiza os confrontos em um dicionário por round/fase
    # Útil para exibir confrontos agrupados por fase no template
    # Exemplo: {1: [conf1, conf2], 2: [conf3, conf4]}
    confrontos_por_round = {}
    max_round = 0  # Rastreia o número máximo de rounds para nomear fases
    
    for conf in confrontos:
        # Se este round não existe no dicionário, cria uma lista vazia
        if conf.round not in confrontos_por_round:
            confrontos_por_round[conf.round] = []
        # Adiciona o confronto à lista do seu round
        confrontos_por_round[conf.round].append(conf)
        # Atualiza qual é o round máximo
        max_round = max(max_round, conf.round)
    
    # Renderiza o template passando todos os dados organizados
    # max_round é usado para nomear as fases dinamicamente:
    # Round 1 = "Primeira Fase"
    # Round max_round = "Final"
    # Round max_round-1 = "Semifinal", etc.
    
    # Pega lista de clientes que ainda não são participantes deste torneio
    clientes_participantes = [p.cliente for p in participantes]
    clientes_disponiveis = Cliente.select().where(~(Cliente.id.in_([c.id for c in clientes_participantes] or [])))
    
    return render_template(
        'detalhe_torneio.html',
        torneio=torneio,  # Objeto do torneio
        participantes=participantes,  # Lista de participantes
        confrontos_por_round=confrontos_por_round,  # Dicionário organizado por round
        total_participantes=len(participantes),  # Contador de participantes
        max_round=max_round,  # Número máximo de rounds
        clientes_disponiveis=clientes_disponiveis  # Clientes que podem ser adicionados
    )


# ─────────────────────────────────────────────────────────────────────────────────
# 4. ADICIONAR NOVO PARTICIPANTE
# ─────────────────────────────────────────────────────────────────────────────────
# URL: POST /torneios/<id>/participante/novo
# O que faz: Adiciona um cliente (já existente) como participante do torneio
# Onde fica: Form em detalhe_torneio.html

@torneio_route.route('/<int:torneio_id>/participante/novo', methods=['POST'])
def novo_participante(torneio_id):
    """Adiciona um cliente como participante do torneio"""
    # Valida se o torneio existe
    try:
        torneio = Torneio.get(Torneio.id == torneio_id)
    except Torneio.DoesNotExist:
        abort(404)
    
    # Pega o ID do cliente enviado pelo formulário
    cliente_id = request.form.get('cliente_id')
    
    # Valida se cliente foi selecionado
    if cliente_id:
        try:
            cliente = Cliente.get_by_id(cliente_id)
            
            # Verifica se o cliente já é participante deste torneio
            participante_existente = Participante.get_or_none(
                (Participante.cliente == cliente) & 
                (Participante.torneio == torneio)
            )
            
            # Se não é participante, adiciona
            if not participante_existente:
                Participante.create(cliente=cliente, torneio=torneio)
        except Cliente.DoesNotExist:
            pass  # Ignora se cliente não existir
    
    # Redireciona de volta à página de detalhes do torneio
    return redirect(url_for('torneio.detalhe_torneio', torneio_id=torneio_id))


# ─────────────────────────────────────────────────────────────────────────────────
# 5. DELETAR PARTICIPANTE
# ─────────────────────────────────────────────────────────────────────────────────
# URL: POST /torneios/<id>/participante/<pid>/deletar
# O que faz: Remove um participante (só funciona se não há bracket criado)
# Onde fica: Botão ✕ ao lado de cada participante em detalhe_torneio.html

@torneio_route.route('/<int:torneio_id>/participante/<int:pid>/deletar', methods=['POST'])
def deletar_participante(torneio_id, pid):
    """Remove um participante do torneio"""
    # Valida se tanto o torneio quanto o participante existem
    try:
        torneio = Torneio.get(Torneio.id == torneio_id)
        participante = Participante.get(Participante.id == pid)
    except (Torneio.DoesNotExist, Participante.DoesNotExist):
        abort(404)
    
    # Verifica se o participante realmente pertence a este torneio
    # (segurança para evitar deletar participante de outro torneio)
    if participante.torneio_id == torneio_id:
        # DELETE: Remove o participante do banco de dados
        participante.delete_instance()
    
    # Redireciona de volta à página de detalhes do torneio
    return redirect(url_for('torneio.detalhe_torneio', torneio_id=torneio_id))


# ─────────────────────────────────────────────────────────────────────────────────
# 6. GERAR BRACKET ALEATÓRIO
# ─────────────────────────────────────────────────────────────────────────────────
# URL: POST /torneios/<id>/gerar-bracket
# O que faz: 
#   1. Embaralha todos os participantes
#   2. Cria confrontos do Round 1 com pares aleatórios
#   3. Apaga qualquer bracket anterior (reseta o torneio)
# Onde fica: Botão "🎯 Bracket Aleatório" em detalhe_torneio.html

@torneio_route.route('/<int:torneio_id>/gerar-bracket', methods=['POST'])
def gerar_bracket(torneio_id):
    """Gera o bracket inicial do torneio com pares ALEATÓRIOS"""
    # Valida se o torneio existe
    try:
        torneio = Torneio.get(Torneio.id == torneio_id)
    except Torneio.DoesNotExist:
        abort(404)
    
    # SELECT: Pega lista de todos os participantes do torneio
    participantes = list(torneio.participantes)
    
    # Validação: precisa de pelo menos 2 participantes
    if len(participantes) < 2:
        return redirect(url_for('torneio.detalhe_torneio', torneio_id=torneio_id))
    
    # DELETE: Apaga todos os confrontos anteriores (reseta o bracket)
    Confronto.delete().where(Confronto.torneio == torneio).execute()
    
    # Embaralha os participantes de forma ALEATÓRIA
    # .copy() faz uma cópia da lista para não modificar a original
    participantes_embaralhados = participantes.copy()
    random.shuffle(participantes_embaralhados)  # Embaralha a lista 
    
    # Cria confrontos do Round 1 percorrendo os participantes em PARES
    # range(0, len, 2) pega índices: 0, 2, 4, 6, ... (progressão de 2 em 2)
    for i in range(0, len(participantes_embaralhados), 2):
        # Participante 1 (sempre existe - é o índice i)
        p1 = participantes_embaralhados[i]
        # Participante 2 (pode ser None se houver número ímpar)
        # Verifica se índice i+1 existe antes de acessar
        p2 = participantes_embaralhados[i + 1] if i + 1 < len(participantes_embaralhados) else None
        
        # INSERT: Cria o confronto no banco de dados
        Confronto.create(
            torneio=torneio,
            participante1=p1,  # Sempre preenchido
            participante2=p2,  # Pode ser None (W.O / vitória automática)
            round=1  # Sempre começa no round 1
        )
    
    # Redireciona de volta à página de detalhes do torneio
    return redirect(url_for('torneio.detalhe_torneio', torneio_id=torneio_id))


# ─────────────────────────────────────────────────────────────────────────────────
# 7. GERAR BRACKET MANUAL (COM SELEÇÃO MANUAL DE ADVERSÁRIOS)
# ─────────────────────────────────────────────────────────────────────────────────
# URL: GET /torneios/<id>/gerar-bracket-manual (formulário) | POST (criar)
# O que faz: 
#   - GET: Exibe formulário para selecionar manualmente os adversários
#   - POST: Cria os confrontos baseado nas seleções do usuário
# Onde fica: Botão "⚙️ Bracket Manual" em detalhe_torneio.html

@torneio_route.route('/<int:torneio_id>/gerar-bracket-manual', methods=['GET', 'POST'])
def gerar_bracket_manual(torneio_id):
    """Gera o bracket permitindo seleção MANUAL de adversários"""
    # Valida se o torneio existe
    try:
        torneio = Torneio.get(Torneio.id == torneio_id)
    except Torneio.DoesNotExist:
        abort(404)
    
    # SELECT: Pega lista de todos os participantes
    participantes = list(torneio.participantes)
    
    # Se o método é POST, significa que o usuário enviou as seleções
    if request.method == 'POST':
        # DELETE: Apaga todos os confrontos anteriores (reseta o bracket)
        Confronto.delete().where(Confronto.torneio == torneio).execute()
        
        # Conta quantos pares o usuário selecionou
        # Conta quantas campos 'par_p1_' existem no formulário
        pares_count = len([k for k in request.form.keys() if k.startswith('par_p1_')])
        
        # Processa cada par selecionado pelo usuário
        # O template gera campos como par_p1_0, par_p2_0, par_p1_1, par_p2_1, etc.
        for i in range(pares_count):
            # Pega o ID do participante 1 (obrigatório)
            p1_id = request.form.get(f'par_p1_{i}')
            # Pega o ID do participante 2 (opcional - pode ser bye)
            p2_id = request.form.get(f'par_p2_{i}')
            
            # Se o participante 1 foi selecionado
            if p1_id:
                try:
                    # SELECT: Busca o participante no banco de dados
                    p1 = Participante.get(Participante.id == int(p1_id))
                    p2 = None
                    
                    # Se participante 2 foi selecionado (p2_id não vazio)
                    if p2_id and p2_id != '':
                        # SELECT: Busca o participante 2
                        p2 = Participante.get(Participante.id == int(p2_id))
                    
                    # INSERT: Cria o confronto com a seleção do usuário
                    Confronto.create(
                        torneio=torneio,
                        participante1=p1,  # Seleção do usuário
                        participante2=p2,  # Seleção do usuário (pode ser None)
                        round=1  # Sempre começa no round 1
                    )
                except Participante.DoesNotExist:
                    # Se algum participante não existir, ignora
                    pass
        
        # Redireciona para a página de detalhes do torneio
        return redirect(url_for('torneio.detalhe_torneio', torneio_id=torneio_id))
    
    # GET: Exibe o formulário de seleção manual
    # Embaralha os participantes
    participantes_embaralhados = participantes.copy()
    random.shuffle(participantes_embaralhados)
    
    # Cria um dicionário com número -> participante (igual ao modo_plateia)
    participantes_numerados = {i + 1: p for i, p in enumerate(participantes_embaralhados)}
    
    return render_template(
        'gerar_bracket_manual.html',
        torneio=torneio,
        participantes=participantes,
        participantes_numerados=participantes_numerados
    )


# ─────────────────────────────────────────────────────────────────────────────────
# 8. REGISTRAR VENCEDOR DE CONFRONTO
# ─────────────────────────────────────────────────────────────────────────────────
# URL: POST /torneios/<id>/confronto/<conf_id>/vencedor
# O que faz: 
#   1. Recebe qual participante venceu
#   2. Marca o vencedor no confronto
#   3. Verifica se TODOS os confrontos do round foram decididos
#   4. Se sim, gera automaticamente o próximo round
#   5. Verifica se há um CAMPEÃO (todos confrontos decididos)
#   6. Se sim, marca o torneio como 'concluido'
# Onde fica: Botões "✓" ao lado de cada participante em detalhe_torneio.html

@torneio_route.route('/<int:torneio_id>/confronto/<int:conf_id>/vencedor', methods=['POST'])
def registrar_vencedor(torneio_id, conf_id):
    """Registra manualmente o vencedor de um confronto"""
    # Valida se torneio e confronto existem
    try:
        torneio = Torneio.get(Torneio.id == torneio_id)
        confronto = Confronto.get(Confronto.id == conf_id)
    except (Torneio.DoesNotExist, Confronto.DoesNotExist):
        abort(404)
    
    # Pega o ID do participante que venceu (enviado pelo botão no template)
    vencedor_id = request.form.get('vencedor_id')
    
    # Se um vencedor foi selecionado
    if vencedor_id:
        try:
            # SELECT: Busca o participante no banco de dados
            vencedor = Participante.get(Participante.id == vencedor_id)
        except Participante.DoesNotExist:
            abort(404)
        
        # UPDATE: Marca o participante como vencedor do confronto
        confronto.vencedor = vencedor
        confronto.save()  # Salva no banco de dados
        
        # ──────────────────────────────────────────────────────────────────────
        # LÓGICA 1: Verificar se todos os confrontos do round foram decididos
        # ──────────────────────────────────────────────────────────────────────
        round_atual = confronto.round
        
        # Conta TOTAL de confrontos no round atual
        total_confrontos_round = Confronto.select().where(
            (Confronto.torneio == torneio) & (Confronto.round == round_atual)
        ).count()
        
        # Conta quantos confrontos do round atual foram decididos
        # Considerando: confrontos com vencedor OU confrontos com W.O (participante2=None)
        confrontos_decididos = Confronto.select().where(
            (Confronto.torneio == torneio) & 
            (Confronto.round == round_atual) & 
            ((Confronto.vencedor.is_null(False)) |  # Tem vencedor
             (Confronto.participante2.is_null(True)))  # Ou é W.O (sem adversário)
        ).count()
        
        # Se TODOS os confrontos do round foram decididos E há mais de 1 confronto
        # (condição: total_confrontos_round > 1 para não gerar próximo round de decisões triviais)
        if total_confrontos_round == confrontos_decididos and total_confrontos_round > 1:
            # Chama a função para gerar o próximo round automaticamente
            gerar_proximo_round(torneio, round_atual)
        
        # ──────────────────────────────────────────────────────────────────────
        # LÓGICA 2: Verificar se há um CAMPEÃO (torneio terminado)
        # ──────────────────────────────────────────────────────────────────────
        
        # Conta TOTAL de confrontos no torneio
        todos_confrontos = Confronto.select().where(Confronto.torneio == torneio)
        total_conf = todos_confrontos.count()
        
        # Conta quantos confrontos DO TORNEIO INTEIRO foram decididos
        # Considerando: confrontos com vencedor OU confrontos com W.O (participante2=None)
        conf_decididos = Confronto.select().where(
            (Confronto.torneio == torneio) & 
            ((Confronto.vencedor.is_null(False)) |  # Tem vencedor
             (Confronto.participante2.is_null(True)))  # Ou é W.O (sem adversário)
        ).count()
        
        # Se TODOS os confrontos do torneio foram decididos
        if total_conf > 0 and total_conf == conf_decididos:
            # UPDATE: Marca o torneio como 'concluido'
            torneio.status = 'concluido'
            torneio.save()  # Salva no banco de dados
    
    # Redireciona de volta à página de detalhes do torneio
    return redirect(url_for('torneio.detalhe_torneio', torneio_id=torneio_id))


# ─────────────────────────────────────────────────────────────────────────────────
# 9. GERAR PRÓXIMO ROUND (AUTOMÁTICO - INTERNO)
# ─────────────────────────────────────────────────────────────────────────────────
# Esta é uma função INTERNA (não é uma rota)
# O que faz: 
#   1. Pega todos os vencedores do round anterior
#   2. Cria confrontos do próximo round com os vencedores em pares
#   3. Se número ímpar de vencedores, um passa direto (bye automático)
# Chamada por: registrar_vencedor (automaticamente)

def gerar_proximo_round(torneio, round_atual):
    """Gera automaticamente os confrontos do próximo round"""
    # SELECT: Busca todos os confrontos decididos do round atual
    # Considerando: com vencedor OU W.O (participante2=None)
    vencedores_round = list(
        Confronto.select()
        .where(
            (Confronto.torneio == torneio) & 
            (Confronto.round == round_atual) &
            ((Confronto.vencedor.is_null(False)) |  # Tem vencedor
             (Confronto.participante2.is_null(True)))  # Ou é W.O (sem adversário)
        )
        .order_by(Confronto.id)  # Ordena por ID para pareamentos ordenados
    )
    
    # Calcula qual será o próximo número de round
    proximo_round = round_atual + 1
    
    # Cria confrontos do próximo round percorrendo os vencedores em PARES
    # range(0, len, 2) pega índices: 0, 2, 4, 6, ... (progressão de 2 em 2)
    for i in range(0, len(vencedores_round), 2):
        # Participante 1 (sempre existe - é o índice i)
        # Se tem vencedor, usa vencedor. Se é W.O (participante2=None), usa participante1
        conf1 = vencedores_round[i]
        p1 = conf1.vencedor if conf1.vencedor else conf1.participante1
        
        # Participante 2 (pode ser None se houver número ímpar)
        if i + 1 < len(vencedores_round):
            conf2 = vencedores_round[i + 1]
            p2 = conf2.vencedor if conf2.vencedor else conf2.participante1
        else:
            p2 = None
        
        # CASO 1: Há dois participantes (pareamento normal)
        if p1 and p2:
            # INSERT: Cria o confronto entre p1 e p2
            Confronto.create(
                torneio=torneio,
                participante1=p1,
                participante2=p2,
                round=proximo_round
            )
        
        # CASO 2: Há apenas um participante (número ímpar de vencedores)
        elif p1:
            # INSERT: Cria um "bye" automático (p1 passa direto)
            # Não marca vencedor - apenas deixa o participante2 como None
            # O sistema considera participante2=None como "passou automaticamente"
            Confronto.create(
                torneio=torneio,
                participante1=p1,
                participante2=None,  # Sem adversário - marca como W.O
                round=proximo_round
                # vencedor NÃO é preenchido - apenas passa automaticamente
            )


# ─────────────────────────────────────────────────────────────────────────────────
# 10. DELETAR TORNEIO
# ─────────────────────────────────────────────────────────────────────────────────
# URL: POST /torneios/<id>/deletar
# O que faz: 
#   1. Deleta TODOS os confrontos do torneio
#   2. Deleta TODOS os participantes do torneio
#   3. Deleta o torneio
#   4. Redireciona para lista de torneios
# Onde fica: Botão "🗑️ Deletar" em listar_torneios.html

@torneio_route.route('/<int:torneio_id>/deletar', methods=['POST'])
def deletar_torneio(torneio_id):
    """Deleta um torneio e TODOS seus dados associados"""
    # Valida se o torneio existe
    try:
        torneio = Torneio.get(Torneio.id == torneio_id)
    except Torneio.DoesNotExist:
        abort(404)
    
    # DELETE: Remove todos os confrontos do torneio
    # Isso garante integridade referencial (sem confrontos órfãos)
    Confronto.delete().where(Confronto.torneio == torneio).execute()
    
    # DELETE: Remove todos os participantes do torneio
    Participante.delete().where(Participante.torneio == torneio).execute()
    
    # DELETE: Remove o torneio em si
    torneio.delete_instance()
    
    # Redireciona para a página de lista de torneios
    return redirect(url_for('torneio.listar_torneios'))


# ─────────────────────────────────────────────────────────────────────────────────
# 11. MODO PLATEIA (SELEÇÃO COM NÚMEROS E REVELAÇÃO DE NOMES)
# ─────────────────────────────────────────────────────────────────────────────────
# URL: GET /torneios/<id>/modo-plateia (formulário) | POST (criar)
# O que faz: 
#   - GET: Exibe uma interface com números embaralhados (nomes ocultos)
#   - Permite selecionar dois números por vez
#   - Revela os nomes quando dois são selecionados
#   - POST: Cria os confrontos baseado nas seleções
# Onde fica: Botão "👥 Modo Plateia" em detalhe_torneio.html

@torneio_route.route('/<int:torneio_id>/modo-plateia', methods=['GET', 'POST'])
def modo_plateia(torneio_id):
    """Modo Plateia: Seleção com números, revelação de nomes ao selecionar dois números"""
    # Valida se o torneio existe
    try:
        torneio = Torneio.get(Torneio.id == torneio_id)
    except Torneio.DoesNotExist:
        abort(404)
    
    # SELECT: Pega lista de todos os participantes
    participantes = list(torneio.participantes)
    
    # Se o método é POST, significa que o usuário finalizou as seleções
    if request.method == 'POST':
        # DELETE: Apaga todos os confrontos anteriores (reseta o bracket)
        Confronto.delete().where(Confronto.torneio == torneio).execute()
        
        # Conta quantos pares o usuário selecionou
        pares_count = len([k for k in request.form.keys() if k.startswith('par_p1_')])
        
        # Processa cada par selecionado pelo usuário
        for i in range(pares_count):
            # Pega o ID do participante 1 (obrigatório)
            p1_id = request.form.get(f'par_p1_{i}')
            # Pega o ID do participante 2 (opcional - pode ser bye)
            p2_id = request.form.get(f'par_p2_{i}')
            
            # Se o participante 1 foi selecionado
            if p1_id:
                try:
                    # SELECT: Busca o participante no banco de dados
                    p1 = Participante.get(Participante.id == int(p1_id))
                    p2 = None
                    
                    # Se participante 2 foi selecionado
                    if p2_id and p2_id != '':
                        # SELECT: Busca o participante 2
                        p2 = Participante.get(Participante.id == int(p2_id))
                    
                    # INSERT: Cria o confronto
                    Confronto.create(
                        torneio=torneio,
                        participante1=p1,
                        participante2=p2,
                        round=1
                    )
                except (Participante.DoesNotExist, ValueError):
                    # Se algum participante não existir, ignora
                    pass
        
        # Redireciona para a página de detalhes do torneio
        return redirect(url_for('torneio.detalhe_torneio', torneio_id=torneio_id))
    
    # GET: Exibe o modo plateia com números embaralhados
    # Embaralha os participantes
    participantes_embaralhados = participantes.copy()
    random.shuffle(participantes_embaralhados)
    
    # Cria um dicionário com número -> participante
    participantes_numerados = {i + 1: p for i, p in enumerate(participantes_embaralhados)}
    
    return render_template(
        'modo_plateia.html',
        torneio=torneio,
        participantes=participantes,
        participantes_numerados=participantes_numerados
    )