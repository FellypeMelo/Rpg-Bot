# Referência de Comandos do Bot RPG

Este documento serve como uma referência completa para todos os comandos disponíveis no bot RPG, incluindo sua sintaxe, descrição e exemplos de uso.

## Convenções
- `<argumento_obrigatório>`: Argumento que deve ser fornecido.
- `[argumento_opcional]`: Argumento opcional.
- `"--flag"`: Uma flag opcional que altera o comportamento do comando.
- `"<texto com espaços>"`: Use aspas duplas para argumentos que contêm espaços.

---

## Módulo: Gerenciamento de Personagens

### `!ficha`
- **Descrição:** Comando base para gerenciar fichas de personagens. Se usado sem subcomando, exibe uma mensagem de ajuda.
- **Uso:** `!ficha`
- **Exemplos:**
  - `!ficha`

### `!ficha criar <nome> <classe> [--alias <apelido>]`
- **Descrição:** Cria uma nova ficha de personagem com o nome e a classe especificados. Um apelido é opcional.
- **Argumentos:**
  - `<nome>`: O nome do personagem (obrigatório, entre aspas se tiver espaços).
  - `<classe>`: A classe do personagem (obrigatório, ex: "Guerreiro", "Mago").
  - `--alias <apelido>`: (Opcional) Um apelido para o personagem.
- **Uso:** `!ficha criar "Meu Herói" Guerreiro --alias "O Bravo"`
- **Exemplos:**
  - `!ficha criar "Arthur Pendragon" Cavaleiro`
  - `!ficha criar "Merlin" Mago --alias "O Enigmático"`

### `!ficha ver <id|nome>`
- **Descrição:** Exibe a ficha completa de um personagem, incluindo atributos, modificadores, maestrias, PH e nível. Pode ser buscado por ID ou nome/apelido.
- **Argumentos:**
  - `<id|nome>`: O ID único do personagem ou o nome/apelido (entre aspas se tiver espaços).
- **Uso:** `!ficha ver <ID_DO_PERSONAGEM>` ou `!ficha ver "Nome do Personagem"`
- **Exemplos:**
  - `!ficha ver 123e4567-e89b-12d3-a456-426614174000`
  - `!ficha ver "Arthur Pendragon"`
  - `!ficha ver "O Bravo"`

### `!ficha atualizar <id> <campo> <valor>`
- **Descrição:** Atualiza um campo específico da ficha de um personagem.
- **Argumentos:**
  - `<id>`: O ID único do personagem.
  - `<campo>`: O nome do campo a ser atualizado (ex: `name`, `alias`, `masteries`).
  - `<valor>`: O novo valor para o campo. Para `masteries`, deve ser uma string JSON de um dicionário (ex: `'{"swords": 3, "archery": 1}'`).
- **Uso:** `!ficha atualizar <ID> name "Novo Nome"`
- **Exemplos:**
  - `!ficha atualizar 123e4567-e89b-12d3-a456-426614174000 name "Sir Arthur"`
  - `!ficha atualizar 123e4567-e89b-12d3-a456-426614174000 alias "Rei Arthur"`
  - `!ficha atualizar 123e4567-e89b-12d3-a456-426614174000 masteries '{"swords": 3, "shields": 2}'`

### `!ficha excluir <id>`
- **Descrição:** Exclui permanentemente uma ficha de personagem. Requer confirmação.
- **Argumentos:**
  - `<id>`: O ID único do personagem.
- **Uso:** `!ficha excluir <ID_DO_PERSONAGEM>`
- **Exemplos:**
  - `!ficha excluir 123e4567-e89b-12d3-a456-426614174000` (o bot pedirá confirmação "sim")

---

## Módulo: Sistema de Nivelamento

### `!up <id> <níveis> [status_points] [mastery_points] [ph_points]`
- **Descrição:** Aplica um ou mais níveis a um personagem, distribuindo pontos de status, maestria e PH.
- **Argumentos:**
  - `<id>`: O ID único do personagem.
  - `<níveis>`: O número de níveis a serem ganhos.
  - `[status_points]`: (Opcional) Uma string JSON de um dicionário com os pontos de status a serem gastos (ex: `'{"strength": 2, "constitution": 1}'`). Padrão: `{}`.
  - `[mastery_points]`: (Opcional) Uma string JSON de um dicionário com os pontos de maestria a serem gastos (ex: `'{"swords": 2}'`). Padrão: `{}`.
  - `[ph_points]`: (Opcional) O número de pontos de PH a serem gastos. Padrão: `0`.
- **Uso:** `!up <ID> 1 '{"strength": 2, "constitution": 1}' '{"swords": 2}' 1`
- **Exemplos:**
  - `!up 123e4567-e89b-12d3-a456-426614174000 1 '{"strength": 2}'`
  - `!up 123e4567-e89b-12d3-a456-426614174000 2 '{}' '{"archery": 1}' 1`
  - `!up 123e4567-e89b-12d3-a456-426614174000 1` (apenas sobe de nível, pontos acumulados)

---

## Módulo: Sistema de Combate

### `!startcombat <ficha_id>`
- **Descrição:** Inicia uma nova sessão de combate para o personagem especificado. Cria uma cópia temporária da ficha.
- **Argumentos:**
  - `<ficha_id>`: O ID único do personagem para iniciar o combate.
- **Uso:** `!startcombat <ID_DO_PERSONAGEM>`
- **Exemplos:**
  - `!startcombat 123e4567-e89b-12d3-a456-426614174000`

### `!dano <session_id> <tipo> <valor>`
- **Descrição:** Aplica dano a um atributo (HP, Chakra, FP) na sessão de combate ativa.
- **Argumentos:**
  - `<session_id>`: O ID da sessão de combate.
  - `<tipo>`: O tipo de atributo a receber dano (`hp`, `chakra`, `fp`).
  - `<valor>`: A quantidade de dano a ser aplicada.
- **Uso:** `!dano <ID_DA_SESSAO> hp 20`
- **Exemplos:**
  - `!dano abcdef12-3456-7890-abcd-ef1234567890 hp 25`
  - `!dano abcdef12-3456-7890-abcd-ef1234567890 chakra 10`

### `!cura <session_id> <tipo> <valor>`
- **Descrição:** Aplica cura a um atributo (HP, Chakra, FP) na sessão de combate ativa. Não pode exceder o valor máximo.
- **Argumentos:**
  - `<session_id>`: O ID da sessão de combate.
  - `<tipo>`: O tipo de atributo a receber cura (`hp`, `chakra`, `fp`).
  - `<valor>`: A quantidade de cura a ser aplicada.
- **Uso:** `!cura <ID_DA_SESSAO> hp 15`
- **Exemplos:**
  - `!cura abcdef12-3456-7890-abcd-ef1234567890 hp 10`
  - `!cura abcdef12-3456-7890-abcd-ef1234567890 fp 5`

### `!endcombat <session_id> [--persist]`
- **Descrição:** Finaliza uma sessão de combate.
- **Argumentos:**
  - `<session_id>`: O ID da sessão de combate a ser finalizada.
  - `--persist`: (Opcional) Se presente, as mudanças feitas nos atributos temporários durante a sessão serão aplicadas à ficha permanente do personagem. Caso contrário, as mudanças serão descartadas.
- **Uso:** `!endcombat <ID_DA_SESSAO>` ou `!endcombat <ID_DA_SESSAO> --persist`
- **Exemplos:**
  - `!endcombat abcdef12-3456-7890-abcd-ef1234567890`
  - `!endcombat abcdef12-3456-7890-abcd-ef1234567890 --persist`

---

## Módulo: Relatórios e Estatísticas

### `!progresso <ficha_id>`
- **Descrição:** Exibe um relatório detalhado do progresso de um personagem, incluindo níveis, atributos, modificadores e pontos disponíveis.
- **Argumentos:**
  - `<ficha_id>`: O ID único do personagem.
- **Uso:** `!progresso <ID_DO_PERSONAGEM>`
- **Exemplos:**
  - `!progresso 123e4567-e89b-12d3-a456-426614174000`

### `!stats`
- **Descrição:** Exibe estatísticas gerais de uso do bot, como o número total de personagens e a distribuição de classes.
- **Uso:** `!stats`
- **Exemplos:**
  - `!stats`

---

## Comando de Ajuda
- **Comando:** `!ajuda [comando]`
- **Descrição:** Exibe informações de ajuda sobre um comando específico ou lista todos os comandos disponíveis.
- **Argumentos:**
  - `[comando]`: (Opcional) O nome de um comando para obter ajuda detalhada.
- **Uso:** `!ajuda` ou `!ajuda ficha`
- **Exemplos:**
  - `!ajuda`
  - `!ajuda ficha criar`
  - `!ajuda up`