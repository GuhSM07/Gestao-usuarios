# ═══════════════════════════════════════════════════════════════════════════════
# ARQUIVO PRINCIPAL DA APLICAÇÃO
# ═══════════════════════════════════════════════════════════════════════════════
# Este é o arquivo de ENTRADA da aplicação
# O que faz:
#   1. Importa o Flask
#   2. Cria a instância da aplicação
#   3. Configura tudo (rotas, banco de dados)
#   4. Inicia o servidor
#
# COMO EXECUTAR: python main.py
# RESULTADO: Servidor Flask inicia em localhost:5000

from flask import Flask  # Framework web
from flask_cors import CORS  # CORS para requisições cruzadas
from configuration import configure_all  # Função que configura TUDO
 

# ─────────────────────────────────────────────────────────────────────────────────
# CRIAR INSTÂNCIA DO FLASK
# ─────────────────────────────────────────────────────────────────────────────────
# __name__ = nome do módulo (usualmente '__main__')
# Isso permite que Flask saiba onde procurar por templates e arquivos estáticos

app = Flask(__name__)

# Habilita CORS para requisições cruzadas (necessário para PWA/APK)
CORS(app)


# ─────────────────────────────────────────────────────────────────────────────────
# CONFIGURAR A APLICAÇÃO
# ─────────────────────────────────────────────────────────────────────────────────
# Chama a função configure_all() que:
#   - Registra as rotas (blueprints)
#   - Conecta ao banco de dados
#   - Cria as tabelas

configure_all(app)


# ─────────────────────────────────────────────────────────────────────────────────
# INICIAR O SERVIDOR
# ─────────────────────────────────────────────────────────────────────────────────
# debug=True significa:
#   - Auto-recarrega quando você modifica o código
#   - Mostra erro traceback completo se algo der ruim
#   - Abre debugger interativo em caso de erro
#
# host='0.0.0.0' permite conexões de qualquer IP na rede
# Acesse em: http://localhost:5000 (local)
#           http://<seu-ip>:5000 (de outro dispositivo na rede)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

