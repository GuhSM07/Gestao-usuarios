# 📚 Documentação Completa - Sistema de Torneios com Chaveamento

## 📋 Índice
1. [Estrutura de Dados](#estrutura-de-dados)
2. [Fluxo de Operações](#fluxo-de-operações)
3. [Modelos de Banco de Dados](#modelos-de-banco-de-dados)
4. [Rotas e Funcionalidades](#rotas-e-funcionalidades)
5. [Lógica de Geração do Bracket](#lógica-de-geração-do-bracket)
6. [Lógica de Registro de Vencedores](#lógica-de-registro-de-vencedores)
7. [Lógica de Próximos Rounds](#lógica-de-próximos-rounds)
8. [Lógica de Nomeação de Fases](#lógica-de-nomeação-de-fases)
9. [Fluxo Completo de um Torneio](#fluxo-completo-de-um-torneio)

---

## 🗄️ Estrutura de Dados

### Modelo 1: Torneio
```python
class Torneio(Model):
    nome = CharField()                              # Nome do torneio (ex: "Torneio de Boxe")
    data_criacao = DateTimeField(default=...)       # Data/hora de criação
    status = CharField(default='em_progresso')      # Status: 'em_progresso' ou 'finalizado'
    
    class Meta:
        database = db
```

**Propósito:** Armazena informações do torneio principal
**Relações:** Um Torneio tem muitos Participantes e muitos Confrontos

---

### Modelo 2: Participante
```python
class Participante(Model):
    nome = CharField()                              # Nome do participante
    torneio = ForeignKeyField(Torneio, ...)        # Referência ao torneio (chave estrangeira)
    data_registro = DateTimeField(default=...)      # Quando foi adicionado
    
    class Meta:
        database = db
```

**Propósito:** Armazena cada participante de um torneio
**Relacionamento:** Muitos Participantes pertencem a Um Torneio

---

### Modelo 3: Confronto
```python
class Confronto(Model):
    torneio = ForeignKeyField(Torneio, ...)                 # Qual torneio
    participante1 = ForeignKeyField(Participante, ..., null=True)  # Primeiro adversário
    participante2 = ForeignKeyField(Participante, ..., null=True)  # Segundo adversário
    vencedor = ForeignKeyField(Participante, ..., null=True)       # Quem venceu (None se não decidido)
    round = IntegerField()                          # Número do round (1, 2, 3...)
    data_confronto = DateTimeField(default=...)     # Quando foi criado
    
    class Meta:
        database = db
```

**Propósito:** Armazena cada confronto/match do torneio
**Relacionamento:** Um Torneio tem muitos Confrontos, cada Confronto tem 2 Participantes

---

## 🔄 Fluxo de Operações

```
┌─────────────────┐
│ Criar Torneio   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│ Adicionar Participantes     │
│ (mínimo 2)                  │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Gerar Bracket               │
│ (embaralha e cria R1)       │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Registrar Vencedor cada     │
│ Confronto do Round 1        │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Sistema Cria Automaticamente │
│ o Round 2 com Vencedores    │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Repetir até Final           │
│ (apenas 1 confronto)        │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│ Campeão Coroado! 👑         │
└─────────────────────────────┘
```

---

## 🛠️ Rotas e Funcionalidades

### 1️⃣ Listar Torneios
```python
@torneio_route.route('/', methods=['GET'])
def listar_torneios():
    """Exibe todos os torneios criados"""
    torneios = Torneio.select()  # Busca TODOS os torneios no BD
    return render_template('listar_torneios.html', torneios=torneios)
```

**O que faz:**
- Busca no banco de dados TODOS os torneios
- Exibe em um template HTML com cards
- Usuário pode ver nome, quantidade de participantes, confrontos e status

---

### 2️⃣ Criar Novo Torneio
```python
@torneio_route.route('/novo', methods=['GET', 'POST'])
def novo_torneio():
    if request.method == 'POST':
        nome = request.form.get('nome')  # Pega o nome do formulário
        if nome:
            torneio = Torneio.create(nome=nome)  # Cria no banco de dados
            return redirect(url_for('torneio.detalhe_torneio', torneio_id=torneio.id))
    return render_template('form_torneio.html')  # Exibe o formulário
```

**O que faz:**
- GET: Exibe formulário para criar torneio
- POST: Recebe o nome e cria um novo Torneio no banco
- Redireciona para a página de detalhes do novo torneio

---

### 3️⃣ Detalhes do Torneio
```python
@torneio_route.route('/<int:torneio_id>', methods=['GET'])
def detalhe_torneio(torneio_id):
    try:
        torneio = Torneio.get(Torneio.id == torneio_id)  # Busca o torneio
    except Torneio.DoesNotExist:
        abort(404)  # Se não encontrar, retorna erro 404
    
    participantes = list(torneio.participantes)  # Todos os participantes DESTE torneio
    confrontos = list(torneio.confrontos.order_by(Confronto.round, Confronto.id))
    
    # Organiza confrontos por round em um dicionário
    confrontos_por_round = {}
    max_round = 0
    for conf in confrontos:
        if conf.round not in confrontos_por_round:
            confrontos_por_round[conf.round] = []
        confrontos_por_round[conf.round].append(conf)
        max_round = max(max_round, conf.round)  # Descobre qual é o último round
    
    return render_template(
        'detalhe_torneio.html',
        torneio=torneio,
        participantes=participantes,
        confrontos_por_round=confrontos_por_round,  # Organizado por round
        total_participantes=len(participantes),
        max_round=max_round  # Necessário para nomear as fases corretamente
    )
```

**O que faz:**
- Busca o torneio específico
- Busca todos os participantes dele
- Busca todos os confrontos dele
- **Organiza confrontos por round** em um dicionário (chave = número do round)
- Descobre qual é o último round para nomeação correta
- Passa tudo para o template renderizar

**Exemplo de `confrontos_por_round`:**
```python
{
    1: [Confronto1, Confronto2, Confronto3],  # Round 1 com 3 confrontos
    2: [Confronto4, Confronto5],               # Round 2 com 2 confrontos
    3: [Confronto6]                            # Round 3 com 1 confronto (final)
}
```

---

### 4️⃣ Adicionar Participante
```python
@torneio_route.route('/<int:torneio_id>/participante/novo', methods=['POST'])
def novo_participante(torneio_id):
    try:
        torneio = Torneio.get(Torneio.id == torneio_id)
    except Torneio.DoesNotExist:
        abort(404)
    
    nome = request.form.get('nome')  # Pega o nome do formulário
    
    if nome:
        # Cria um novo Participante linkado a este torneio
        Participante.create(nome=nome, torneio=torneio)
    
    # Volta para a página do torneio
    return redirect(url_for('torneio.detalhe_torneio', torneio_id=torneio_id))
```

**O que faz:**
- Recebe o nome do participante via formulário
- Cria um novo Participante no banco
- **Importante:** Vincula ao torneio específico via `torneio=torneio`
- Volta para a página do torneio (agora com 1 participante a mais)

---

### 5️⃣ Deletar Participante
```python
@torneio_route.route('/<int:torneio_id>/participante/<int:pid>/deletar', methods=['POST'])
def deletar_participante(torneio_id, pid):
    try:
        torneio = Torneio.get(Torneio.id == torneio_id)
        participante = Participante.get(Participante.id == pid)
    except (Torneio.DoesNotExist, Participante.DoesNotExist):
        abort(404)
    
    # Verifica se o participante pertence a este torneio
    if participante.torneio_id == torneio_id:
        participante.delete_instance()  # Delete do banco de dados
    
    return redirect(url_for('torneio.detalhe_torneio', torneio_id=torneio_id))
```

**O que faz:**
- Busca o participante
- Valida se pertence ao torneio (segurança)
- Deleta do banco de dados
- Volta para a página do torneio

**IMPORTANTE:** Só funciona se não tiver bracket gerado ainda

---

## 🎯 Lógica de Geração do Bracket

```python
@torneio_route.route('/<int:torneio_id>/gerar-bracket', methods=['POST'])
def gerar_bracket(torneio_id):
    """Gera o bracket inicial do torneio"""
    try:
        torneio = Torneio.get(Torneio.id == torneio_id)
    except Torneio.DoesNotExist:
        abort(404)
    
    participantes = list(torneio.participantes)  # Lista de todos os participantes
    
    # VALIDAÇÃO: Precisa de pelo menos 2 participantes
    if len(participantes) < 2:
        return redirect(url_for('torneio.detalhe_torneio', torneio_id=torneio_id))
    
    # LIMPEZA: Remove confrontos antigos se existirem
    Confronto.delete().where(Confronto.torneio == torneio).execute()
    
    # EMBARALHAMENTO: Cria cópia e embaralha aleatoriamente
    participantes_embaralhados = participantes.copy()
    random.shuffle(participantes_embaralhados)  # Modifica a lista em lugar
    
    # CRIAÇÃO DE CONFRONTOS: Agrupa em pares
    for i in range(0, len(participantes_embaralhados), 2):
        p1 = participantes_embaralhados[i]
        p2 = participantes_embaralhados[i + 1] if i + 1 < len(participantes_embaralhados) else None
        
        Confronto.create(
            torneio=torneio,
            participante1=p1,
            participante2=p2,
            round=1  # Todos no round 1
        )
    
    return redirect(url_for('torneio.detalhe_torneio', torneio_id=torneio_id))
```

### 📊 Exemplo Prático:

**Entrada:** 5 participantes
```
["Alice", "Bob", "Charlie", "David", "Eva"]
```

**Após embaralho aleatório (exemplo):**
```
["Charlie", "Eva", "Alice", "Bob", "David"]
```

**Confrontos criados (Round 1):**
```
Confronto 1: Charlie vs Eva
Confronto 2: Alice vs Bob
Confronto 3: David vs (ninguém) → David recebe bye (avança automaticamente)
```

**Lógica do loop `range(0, 5, 2)`:**
- i=0: p1=Charlie(0), p2=Eva(1) → Cria confronto
- i=2: p1=Alice(2), p2=Bob(3) → Cria confronto
- i=4: p1=David(4), p2=None(não existe) → Cria confronto com p2=None (bye)

---

## 🏆 Lógica de Registro de Vencedores

```python
@torneio_route.route('/<int:torneio_id>/confronto/<int:conf_id>/vencedor', methods=['POST'])
def registrar_vencedor(torneio_id, conf_id):
    """Registra o vencedor de um confronto"""
    try:
        torneio = Torneio.get(Torneio.id == torneio_id)
        confronto = Confronto.get(Confronto.id == conf_id)
    except (Torneio.DoesNotExist, Confronto.DoesNotExist):
        abort(404)
    
    vencedor_id = request.form.get('vencedor_id')  # Pega o ID do botão clicado
    
    if vencedor_id:
        try:
            vencedor = Participante.get(Participante.id == vencedor_id)
        except Participante.DoesNotExist:
            abort(404)
        
        # ✅ REGISTRA O VENCEDOR
        confronto.vencedor = vencedor
        confronto.save()  # Salva no banco de dados
        
        # 🔍 VERIFICA SE TODOS OS CONFRONTOS DO ROUND FORAM DECIDIDOS
        round_atual = confronto.round
        
        # Conta total de confrontos deste round
        total_confrontos_round = Confronto.select().where(
            (Confronto.torneio == torneio) & (Confronto.round == round_atual)
        ).count()
        
        # Conta confrontos com vencedor definido
        confrontos_decididos = Confronto.select().where(
            (Confronto.torneio == torneio) & 
            (Confronto.round == round_atual) & 
            (Confronto.vencedor.is_null(False))  # Que têm vencedor
        ).count()
        
        # 🤖 SE TODOS FORAM DECIDIDOS, GERA PRÓXIMO ROUND AUTOMATICAMENTE
        if total_confrontos_round == confrontos_decididos and total_confrontos_round > 1:
            gerar_proximo_round(torneio, round_atual)
    
    return redirect(url_for('torneio.detalhe_torneio', torneio_id=torneio_id))
```

### 🧮 Exemplo Prático:

**Round 1:**
```
Confronto 1: Alice vs Bob       [Vencedor: Alice] ✅
Confronto 2: Charlie vs David   [Vencedor: David] ✅
Confronto 3: Eva vs (bye)       [Vencedor: Eva] ✅

Total: 3 confrontos
Decididos: 3 confrontos

3 == 3 e 3 > 1?  ✅ SIM!  →  Gera Round 2 automaticamente
```

**Round 2 é criado com:**
```
Confronto 4: Alice vs David
Confronto 5: Eva vs (bye)
```

### ⚠️ Condições para Gerar Próximo Round:

1. **Todos os confrontos do round devem estar decididos**
2. **Deve haver mais de 1 confronto no round atual**
   - Se há apenas 1 confronto e foi decidido, é a FINAL, não gera mais

---

## 🔄 Lógica de Próximos Rounds

```python
def gerar_proximo_round(torneio, round_atual):
    """Gera os confrontos do próximo round automaticamente"""
    
    # 1️⃣ BUSCA TODOS OS VENCEDORES DO ROUND ANTERIOR
    vencedores_round = list(
        Confronto.select()
        .where(
            (Confronto.torneio == torneio) & 
            (Confronto.round == round_atual) &
            (Confronto.vencedor.is_null(False))  # Que têm vencedor
        )
        .order_by(Confronto.id)  # Mantém ordem para pairing justo
    )
    
    proximo_round = round_atual + 1
    
    # 2️⃣ AGRUPA VENCEDORES EM PARES
    for i in range(0, len(vencedores_round), 2):
        p1 = vencedores_round[i].vencedor      # Primeiro vencedor
        p2 = vencedores_round[i + 1].vencedor if i + 1 < len(vencedores_round) else None
        
        # CASO 1: Há 2 participantes (pairing normal)
        if p1 and p2:
            Confronto.create(
                torneio=torneio,
                participante1=p1,
                participante2=p2,
                round=proximo_round
            )
        
        # CASO 2: Sobrou 1 participante (número ímpar)
        elif p1:
            # Cria confronto onde já é conhecida a vitória
            Confronto.create(
                torneio=torneio,
                participante1=p1,
                participante2=None,
                round=proximo_round,
                vencedor=p1  # 🤖 AUTOMÁTICO! Recebe bye
            )
```

### 📊 Exemplo com 3 Vencedores:

**Round 1 Vencedores:**
```
Confronto 1: ✅ Vencedor = Alice
Confronto 2: ✅ Vencedor = Bob
Confronto 3: ✅ Vencedor = Charlie
```

**Loop de pairing:**
```
i=0:
  p1 = Alice (vencedor[0])
  p2 = Bob (vencedor[1])
  → Cria: Alice vs Bob (Round 2)

i=2:
  p1 = Charlie (vencedor[2])
  p2 = None (não existe vencedor[3])
  → Cria: Charlie vs None com vencedor=Charlie (Round 2 - bye automático)
```

**Round 2 será:**
```
Confronto 4: Alice vs Bob       [Pendente de decisão]
Confronto 5: Charlie vs (bye)   [Automaticamente vencido por Charlie]
```

---

## 🏷️ Lógica de Nomeação de Fases

### No Python (routes/torneio.py):

```python
max_round = 0  # Inicializa
for conf in confrontos:
    max_round = max(max_round, conf.round)  # Descobre o número do último round
    
# Passa para o template
render_template(..., max_round=max_round)
```

### No Template (detalhe_torneio.html):

```html
{% for round_num in confrontos_por_round|sort %}
    <h3 class="round-title">
        {% if round_num == 1 %}
            🥊 Primeira Fase
        {% elif round_num == max_round %}
            👑 Final
        {% elif round_num == max_round - 1 %}
            ⚡ Semifinal
        {% elif round_num == max_round - 2 %}
            🔷 Quarterfinal
        {% else %}
            Round {{ round_num }}
        {% endif %}
    </h3>
{% endfor %}
```

### 📊 Exemplos:

**Caso 1: 2 Participantes (1 round total)**
```
Round 1 = 1
max_round = 1

round_num == 1?  ✅ → "Primeira Fase"
round_num == max_round (1)?  ✅ → "Final"
Resultado: "Primeira Fase" (primeira condição tem prioridade)
```

**Caso 2: 4 Participantes (2 rounds total)**
```
Round 1 = 1
Round 2 = 2
max_round = 2

Round 1:
  round_num == 1?  ✅ → "Primeira Fase"

Round 2:
  round_num == 1?  ❌
  round_num == max_round (2)?  ✅ → "Final"
```

**Caso 3: 8 Participantes (3 rounds total)**
```
Round 1 = 1
Round 2 = 2
Round 3 = 3
max_round = 3

Round 1:
  round_num == 1?  ✅ → "Primeira Fase"

Round 2:
  round_num == 1?  ❌
  round_num == max_round (3)?  ❌
  round_num == max_round - 1 (2)?  ✅ → "Semifinal"

Round 3:
  round_num == 1?  ❌
  round_num == max_round (3)?  ✅ → "Final"
```

**Caso 4: 16 Participantes (4 rounds total)**
```
Round 1: "Primeira Fase"
Round 2: "Quarterfinal" (max_round - 2 = 4 - 2 = 2)
Round 3: "Semifinal" (max_round - 1 = 4 - 1 = 3)
Round 4: "Final" (max_round = 4)
```

---

## 🎪 Fluxo Completo de um Torneio

### Passo a Passo Detalhado com 4 Participantes

#### 1️⃣ **Criar Torneio**
```
POST /torneios/novo
Dados: nome = "Torneio de Exemplos"

Resultado no BD:
┌──────────────────────┐
│ Torneio              │
├──────────────────────┤
│ id: 1                │
│ nome: "Exemplos"     │
│ status: em_progresso │
└──────────────────────┘
```

---

#### 2️⃣ **Adicionar Participantes**
```
POST /torneios/1/participante/novo (4 vezes)

Dados:
1. nome = "Alice"
2. nome = "Bob"
3. nome = "Charlie"
4. nome = "David"

Resultado no BD:
┌─────────────────────────────┐
│ Participante                │
├──────┬───────────┬──────────┤
│ id   │ nome      │ torneio  │
├──────┼───────────┼──────────┤
│ 1    │ Alice     │ 1        │
│ 2    │ Bob       │ 1        │
│ 3    │ Charlie   │ 1        │
│ 4    │ David     │ 1        │
└──────┴───────────┴──────────┘
```

---

#### 3️⃣ **Gerar Bracket**
```
POST /torneios/1/gerar-bracket

Processamento:
- Pega 4 participantes
- Embaralha: [Charlie, Alice, David, Bob]
- Cria confrontos do Round 1

Resultado no BD:
┌─────────────────────────────────────────────┐
│ Confronto                                   │
├────┬──────────┬──────────┬───────┬─────────┤
│ id │ p1       │ p2       │ round │ vencedor│
├────┼──────────┼──────────┼───────┼─────────┤
│ 1  │ Charlie  │ Alice    │ 1     │ NULL    │
│ 2  │ David    │ Bob      │ 1     │ NULL    │
└────┴──────────┴──────────┴───────┴─────────┘
```

**Interface mostra:**
```
🥊 Primeira Fase
  ┌──────────────────────┐
  │ Charlie vs Alice     │
  │ [✓ Charlie] [✓ Alice]│
  └──────────────────────┘
  
  ┌──────────────────────┐
  │ David vs Bob         │
  │ [✓ David] [✓ Bob]    │
  └──────────────────────┘
```

---

#### 4️⃣ **Usuário Clica: Charlie vence**
```
POST /torneios/1/confronto/1/vencedor
Dados: vencedor_id = 3 (Charlie)

Processamento:
1. Busca confronto 1
2. Define confronto.vencedor = Charlie
3. Salva no BD
4. Verifica: Total R1 = 2, Decididos = 1
5. 1 ≠ 2, não gera R2 ainda

Resultado no BD:
┌──────────────────────────────────────┐
│ Confronto (Atualizado)               │
├────┬──────────┬────────┬───────┬─────┤
│ id │ p1       │ p2     │ round │ venc│
├────┼──────────┼────────┼───────┼─────┤
│ 1  │ Charlie  │ Alice  │ 1     │ 3   │ ← Atualizado!
│ 2  │ David    │ Bob    │ 1     │NULL │ ← Ainda não
└────┴──────────┴────────┴───────┴─────┘
```

---

#### 5️⃣ **Usuário Clica: David vence**
```
POST /torneios/1/confronto/2/vencedor
Dados: vencedor_id = 1 (David)

Processamento:
1. Busca confronto 2
2. Define confronto.vencedor = David
3. Salva no BD
4. Verifica: Total R1 = 2, Decididos = 2
5. 2 == 2 e 2 > 1? ✅ GERA ROUND 2 AUTOMATICAMENTE!

Detalhes da geração de R2:
  - Busca vencedores do R1: [Charlie, David]
  - i=0: p1=Charlie, p2=David → Cria confronto 3
  - i=2: (fim do loop)

Resultado no BD:
┌────────────────────────────────────────────┐
│ Confronto (Completo)                       │
├────┬────────────┬────────┬───────┬────────┤
│ id │ p1         │ p2     │ round │ vencedor
├────┼────────────┼────────┼───────┼────────┤
│ 1  │ Charlie    │ Alice  │ 1     │ 3      │
│ 2  │ David      │ Bob    │ 1     │ 1      │
│ 3  │ Charlie    │ David  │ 2     │ NULL   │ ← Novo!
└────┴────────────┴────────┴───────┴────────┘
```

**Interface mostra:**
```
🥊 Primeira Fase
  ✅ Decidido: Charlie venceu
  ✅ Decidido: David venceu

⚡ Semifinal (auto-gerada!)
  ┌──────────────────────┐
  │ Charlie vs David     │
  │ [✓ Charlie] [✓ David]│
  └──────────────────────┘
```

---

#### 6️⃣ **Usuário Clica: Charlie vence a Semifinal**
```
POST /torneios/1/confronto/3/vencedor
Dados: vencedor_id = 3 (Charlie)

Processamento:
1. Busca confronto 3
2. Define confronto.vencedor = Charlie
3. Salva no BD
4. Verifica: Total R2 = 1, Decididos = 1
5. 1 == 1 e 1 > 1? ❌ NÃO! (1 não é > 1)
6. Não gera R3 (é a final!)

Resultado no BD:
┌─────────────────────────────────────────┐
│ Confronto (Final)                       │
├────┬────────────┬────────┬───────┬──────┤
│ id │ p1         │ p2     │ round │ venc │
├────┼────────────┼────────┼───────┼──────┤
│ 1  │ Charlie    │ Alice  │ 1     │ 3    │
│ 2  │ David      │ Bob    │ 1     │ 1    │
│ 3  │ Charlie    │ David  │ 2     │ 3    │ ← Atualizado!
└────┴────────────┴────────┴───────┴──────┘
```

**Interface mostra:**
```
🥊 Primeira Fase
  ✅ Decidido: Charlie venceu
  ✅ Decidido: David venceu

⚡ Semifinal
  ✅ Decidido: Charlie venceu

🏆 CAMPEÃO 🏆
   Charlie ✨
```

---

## 🔐 Validações e Segurança

### 1. **Validação de Existência**
```python
try:
    torneio = Torneio.get(Torneio.id == torneio_id)
except Torneio.DoesNotExist:
    abort(404)  # Retorna erro 404 se não encontrar
```

### 2. **Validação de Pertencimento**
```python
if participante.torneio_id == torneio_id:
    participante.delete_instance()  # Só deleta se pertence ao torneio
```

### 3. **Validação de Quantidade Mínima**
```python
if len(participantes) < 2:
    return redirect(...)  # Não gera bracket com menos de 2
```

---

## 📊 Resumo Visual da Arquitetura

```
┌─────────────────────────────────────────────┐
│         Interface Web (Templates)           │
│  ├─ index.html (Dashboard)                  │
│  ├─ listar_torneios.html                    │
│  ├─ form_torneio.html                       │
│  └─ detalhe_torneio.html (Principal)        │
└───────────────────┬─────────────────────────┘
                    │ (Requisições HTTP)
┌───────────────────▼─────────────────────────┐
│         Rotas Flask (routes/torneio.py)     │
│  ├─ listar_torneios()                       │
│  ├─ novo_torneio()                          │
│  ├─ detalhe_torneio()                       │
│  ├─ novo_participante()                     │
│  ├─ deletar_participante()                  │
│  ├─ gerar_bracket()          ◄─ Lógica     │
│  ├─ registrar_vencedor()     ◄─ Principal  │
│  ├─ gerar_proximo_round()    ◄─            │
│  └─ deletar_torneio()                       │
└───────────────────┬─────────────────────────┘
                    │ (Query/Insert/Update)
┌───────────────────▼─────────────────────────┐
│     Banco de Dados SQLite (Peewee ORM)      │
│  ├─ Torneio (table)                         │
│  ├─ Participante (table)                    │
│  └─ Confronto (table)                       │
└─────────────────────────────────────────────┘
```

---

## 🎓 Pontos-Chave para Estudar

### ✅ O que funciona bem:
1. **Lógica de geração automática de rounds** - muito inteligente
2. **Embaralhamento aleatório** - garante justiça
3. **Tratamento de participantes ímpares** - bye automático
4. **Nomeação dinâmica de fases** - funciona para qualquer número de participantes
5. **Validações robustas** - segurança contra erros

### ⚠️ Possíveis melhorias:
1. **Validar dados no frontend** - JavaScript antes de enviar
2. **Adicionar confirmação** - antes de deletar
3. **Histórico de bracket** - guardar versões anteriores
4. **Ranking de participantes** - estatísticas
5. **Seeding** - definir participantes favoritos em posições específicas
6. **Tabela de desempenho** - mostrar histórico do participante

---

## 🚀 Como Testar Localmente

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Iniciar servidor
python main.py

# 3. Acessar
http://127.0.0.1:5000

# 4. Testar fluxo:
#    - Criar torneio
#    - Adicionar 4-8 participantes
#    - Gerar bracket (note o embaralhamento)
#    - Registrar vencedores
#    - Ver geração automática de rounds
```

---

## 📞 Dúvidas Frequentes

**P: Por que usar `random.shuffle()`?**
R: Para embaralhar a lista em seu local, evitando criar cópias desnecessárias.

**P: E se tiver número ímpar de participantes?**
R: Fica `p2 = None` e cria um "bye" automático, o participante avança sozinho.

**P: Pode deletar participante depois de gerar bracket?**
R: Não é bloqueado no código, mas causaria inconsistência. Deveria ser validado.

**P: Como o sistema sabe quando parar de gerar rounds?**
R: Quando há apenas 1 confronto no round, a condição `total_confrontos_round > 1` fica falsa.

**P: E se tiver 3 participantes?**
R: Round 1 = 2 confrontos (2 pares) → 2 vencedores → Round 2 = 1 confronto (final)

---

**Documento criado em:** 29/08/2026  
**Versão:** 1.0  
**Status:** Completo e Detalhado ✅
