# ═══════════════════════════════════════════════════════════════════════════════
# API PARA SINCRONIZAÇÃO OFFLINE - Endpoints JSON
# ═══════════════════════════════════════════════════════════════════════════════
# Rotas para carregamento de dados offline e sincronização

from flask import Blueprint, jsonify, request
from database.models.cliente import Cliente
from database.models.torneio import Torneio, Participante, Confronto
from database.database import db

# Cria um Blueprint para as rotas de API
api_route = Blueprint('api', __name__, url_prefix='/api')


# ─────────────────────────────────────────────────────────────────────────────────
# 1. ENDPOINTS PARA CARREGAR DADOS (GET)
# ─────────────────────────────────────────────────────────────────────────────────

@api_route.route('/clientes-json', methods=['GET'])
def get_clientes_json():
    """Retorna todos os clientes em JSON para cache offline"""
    try:
        clientes = list(Cliente.select())
        dados = [
            {
                'id': c.id,
                'nome': c.nome,
                'email': c.email,
                'telefone': c.telefone
            }
            for c in clientes
        ]
        return jsonify(dados)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_route.route('/torneios-json', methods=['GET'])
def get_torneios_json():
    """Retorna todos os torneios em JSON para cache offline"""
    try:
        torneios = list(Torneio.select())
        dados = [
            {
                'id': t.id,
                'nome': t.nome,
                'status': 'ativo',  # Você pode adicionar um campo status se quiser
                'data_criacao': t.data_criacao.isoformat() if hasattr(t, 'data_criacao') else None
            }
            for t in torneios
        ]
        return jsonify(dados)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_route.route('/participantes-json', methods=['GET'])
def get_participantes_json():
    """Retorna todos os participantes em JSON para cache offline"""
    try:
        participantes = list(Participante.select())
        dados = [
            {
                'id': p.id,
                'torneio_id': p.torneio_id,
                'cliente_id': p.cliente_id,
                'cliente_nome': p.cliente.nome
            }
            for p in participantes
        ]
        return jsonify(dados)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api_route.route('/confrontos-json', methods=['GET'])
def get_confrontos_json():
    """Retorna todos os confrontos em JSON para cache offline"""
    try:
        confrontos = list(Confronto.select())
        dados = [
            {
                'id': c.id,
                'torneio_id': c.torneio_id,
                'participante1_id': c.participante1_id,
                'participante2_id': c.participante2_id,
                'vencedor_id': c.vencedor_id,
                'round': c.round
            }
            for c in confrontos
        ]
        return jsonify(dados)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────────
# 2. ENDPOINT DE SINCRONIZAÇÃO (POST)
# ─────────────────────────────────────────────────────────────────────────────────

@api_route.route('/sync', methods=['POST'])
def sync_data():
    """
    Recebe dados do app offline e sincroniza com o servidor
    
    Formato esperado:
    {
        "timestamp": 1234567890,
        "action": "create|update|delete",
        "store": "clientes|torneios|participantes|confrontos",
        "data": { ... dados ... },
        "synced": false
    }
    """
    try:
        sync_item = request.json
        action = sync_item.get('action')
        store = sync_item.get('store')
        data = sync_item.get('data')

        if action == 'create':
            if store == 'clientes':
                Cliente.create(
                    nome=data.get('nome'),
                    email=data.get('email'),
                    telefone=data.get('telefone')
                )
            elif store == 'torneios':
                Torneio.create(nome=data.get('nome'))
            # ... outros stores ...

        elif action == 'update':
            if store == 'clientes':
                cliente = Cliente.get_by_id(data.get('id'))
                cliente.nome = data.get('nome')
                cliente.email = data.get('email')
                cliente.telefone = data.get('telefone')
                cliente.save()
            elif store == 'torneios':
                torneio = Torneio.get_by_id(data.get('id'))
                torneio.nome = data.get('nome')
                torneio.save()
            # ... outros stores ...

        elif action == 'delete':
            if store == 'clientes':
                Cliente.get_by_id(data.get('id')).delete_instance()
            elif store == 'torneios':
                Torneio.get_by_id(data.get('id')).delete_instance()
            # ... outros stores ...

        return jsonify({'success': True, 'message': f'{action} realizado com sucesso'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────────
# 3. ENDPOINT DE FALLBACK OFFLINE
# ─────────────────────────────────────────────────────────────────────────────────

@api_route.route('/offline-fallback', methods=['GET'])
def offline_fallback():
    """Página de fallback quando app está offline"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Modo Offline</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                margin: 0;
                background: #f5f5f5;
            }
            .offline-container {
                background: white;
                padding: 40px;
                border-radius: 8px;
                text-align: center;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                max-width: 400px;
            }
            .offline-container h1 {
                color: #e74c3c;
                margin-bottom: 10px;
            }
            .offline-container p {
                color: #666;
                line-height: 1.6;
            }
            .status-icon {
                font-size: 48px;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="offline-container">
            <div class="status-icon">📱 ⚠️ 🌐</div>
            <h1>Você está OFFLINE</h1>
            <p>
                A página solicitada não está disponível no cache.<br>
                <strong>Conecte-se à internet</strong> ou use as páginas em cache.
            </p>
        </div>
    </body>
    </html>
    ''', 200, {'Content-Type': 'text/html'}
