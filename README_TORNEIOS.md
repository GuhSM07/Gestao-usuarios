# 🎯 Sistema de Gerenciamento de Torneios por Chaveamento

Bem-vindo! Este sistema permite criar e gerenciar torneios com confrontos por chaveamento (bracket tournament).

## 📋 Funcionalidades Implementadas

### 1. **Gerenciamento de Torneios**
- ✅ Criar novo torneio
- ✅ Listar todos os torneios
- ✅ Visualizar detalhes de cada torneio
- ✅ Deletar torneios

### 2. **Gerenciamento de Participantes**
- ✅ Adicionar participantes a um torneio
- ✅ Visualizar lista de participantes
- ✅ Deletar participantes (antes de gerar o bracket)

### 3. **Sistema de Confrontos (Bracket)**
- ✅ Gerar bracket automaticamente baseado no número de participantes
- ✅ Organizar em múltiplos rounds (Primeira Fase → Semifinal → Final)
- ✅ Registrar manualmente o vencedor de cada confronto
- ✅ Gerar automaticamente o próximo round quando todos os confrontos são decididos
- ✅ Identificar e exibir o campeão final

## 🚀 Como Usar

### Iniciar a Aplicação
```bash
cd /workspaces/Gestao-usuarios
python main.py
```

A aplicação estará disponível em: `http://127.0.0.1:5000`

### Passo a Passo para Criar um Torneio

#### 1. Criar um Novo Torneio
- Clique em "Torneios" na navbar
- Clique no botão "➕ Novo Torneio"
- Digite o nome do torneio
- Clique em "✅ Criar Torneio"

#### 2. Adicionar Participantes
- Na página do torneio, adicione os participantes um por um
- Digite o nome e clique em "Adicionar"
- Você pode adicionar quantos participantes desejar

#### 3. Gerar Bracket
- Após adicionar pelo menos 2 participantes
- Clique no botão "🎯 Gerar Bracket"
- O sistema criará os confrontos da primeira fase automaticamente

#### 4. Registrar Vencedores
- Na seção "⚔️ Confrontos", veja todos os confrontos
- Para cada confronto pendente, clique no ✓ do vencedor
- Após decidir todos os confrontos de um round, o próximo round é criado automaticamente
- Continue até chegar ao campeão final

### Exemplo de Bracket

**Primeira Fase** (4 participantes)
```
Participante A vs Participante B  →  Vencedor: A
Participante C vs Participante D  →  Vencedor: C
```

**Semifinal** (2 vencedores)
```
A vs C  →  Vencedor: A
```

**Final** (1 confronto)
```
A é declarado CAMPEÃO! 👑
```

## 📦 Estrutura de Dados

### Modelo de Dados
- **Torneio**: Nome, data de criação, status
- **Participante**: Nome, referência ao torneio
- **Confronto**: Participante 1, Participante 2, Vencedor, Round, Data

## 🗄️ Banco de Dados
- Tipo: SQLite
- Arquivo: `customermanager.db`
- Tabelas: `cliente`, `torneio`, `participante`, `confronto`

## 📁 Arquivos Adicionados/Modificados

### Novos Arquivos:
- `database/models/torneio.py` - Modelos de dados
- `routes/torneio.py` - Rotas da aplicação
- `templates/base.html` - Template base com navbar
- `templates/listar_torneios.html` - Listagem de torneios
- `templates/form_torneio.html` - Formulário para criar torneio
- `templates/detalhe_torneio.html` - Detalhes e gerenciamento do torneio
- `requirements.txt` - Dependências Python

### Modificados:
- `configuration.py` - Adicionado import dos novos modelos e rotas
- `main.py` - Sem alterações (compatível)

## 🎨 Interface Visual

A aplicação possui:
- **Navbar** com navegação entre seções
- **Cards** para visualizar torneios
- **Formulários** intuitivos para adicionar dados
- **Indicadores visuais** (badges, cores) para status
- **Design responsivo** que se adapta a diferentes tamanhos de tela
- **Emoji** para melhor comunicação visual

## ⚙️ Requisitos

- Python 3.7+
- Flask 2.3.0
- Peewee 3.16.2

## 🔧 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'flask'"
```bash
pip install -r requirements.txt
```

### Erro: Banco de dados não encontrado
- O banco é criado automaticamente ao iniciar a aplicação
- Arquivo: `customermanager.db`

### Porta 5000 já em uso
```bash
# Modificar em main.py:
app.run(debug=True, port=5001)  # Use outra porta
```

## 📝 Notas Importantes

1. **Validação**: O sistema valida automaticamente o número de participantes
2. **Bracket Automático**: O sistema gera os confrontos automaticamente com base na quantidade de participantes
3. **Resultados**: Todos os confrontos e vencedores são registrados no banco de dados
4. **Histórico**: Você pode visualizar todos os torneios passados
5. **Deleção**: Deletar um torneio também deleta todos seus participantes e confrontos

## 🎯 Funcionalidades Futuras Possíveis

- Embaralhamento automático de participantes
- Ranking de vencedores
- Histórico detalhado de resultados
- Exportação de bracket como PDF
- Busca e filtros avançados
- Sistema de pontos/placar
- Integração com redes sociais

---

**Versão**: 1.0  
**Data**: 29/08/2026  
**Desenvolvido por**: Seu Nome  
**Status**: ✅ Funcional
