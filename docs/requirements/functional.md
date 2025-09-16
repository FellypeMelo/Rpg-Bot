# Requisitos Funcionais (RFs)

Este documento detalha os requisitos funcionais para o bot Discord de gerenciamento de fichas de RPG.

## Módulo: Gerenciamento de Personagens

### RF-01: Criar Personagem
- **Comando:** `!ficha criar`
- **Descrição:** Um assistente interativo para criar um personagem com os seguintes campos: nome, apelido (opcional), classe e atributos base (Força, Destreza, Constituição, Inteligência, Sabedoria, Carisma).
- **Campos Calculados:** Modificadores, HP/Chakra/FP (Pontos de Vida/Chakra/Foco) baseados na fórmula da classe.
- **Validação:** Todos os campos devem ser validados antes de salvar o personagem.
- **Critério de Aceitação:** O personagem é persistido com todos os campos corretamente armazenados no sistema.

### RF-02: Visualizar Personagem
- **Comando:** `!ficha ver <id|nome>`
- **Descrição:** Exibe a ficha completa do personagem, incluindo atributos base, modificadores, maestrias, PH (Pontos de Habilidade) e nível.
- **Critério de Aceitação:** Os dados são recuperados e formatados corretamente para exibição no Discord.

### RF-03: Atualizar Personagem
- **Comando:** `!ficha atualizar <campo> <valor>`
- **Descrição:** Permite a atualização de campos específicos do personagem, como nome, apelido e maestrias.
- **Validação:** Os campos a serem atualizados devem ser validados.
- **Critério de Aceitação:** Os campos são atualizados corretamente no sistema.

### RF-04: Excluir Personagem
- **Comando:** `!ficha excluir <id>`
- **Descrição:** Requer uma confirmação explícita do usuário antes de excluir permanentemente um personagem.
- **Critério de Aceitação:** O personagem é completamente removido do sistema após a confirmação.

## Módulo: Sistema de Nivelamento

### RF-05: Aplicar Upagem
- **Comando:** `!up <níveis> <pts_status> <pts_maestria> <pts_ph>`
- **Descrição:** Aplica um ou mais níveis ao personagem, distribuindo pontos de status, maestria e PH.
- **Validação:** Verifica se o PH é suficiente e se os pontos são distribuídos corretamente.
- **Cálculos:** Recalcula novos atributos, modificadores e HP/Chakra/FP.
- **Regra de Negócio:** Para cada nível ganho: 3 pontos de status, 2 pontos de maestria, 1 ponto de PH.
- **Critério de Aceitação:** Todos os cálculos são corretos e consistentes com as regras do sistema de RPG.

### RF-06: Calcular Modificadores
- **Fórmula:** `modificador = floor((Status / 3) - 1)` para todos os atributos (Força, Destreza, Constituição, Inteligência, Sabedoria, Carisma).
- **Descrição:** Os modificadores devem ser recalculados automaticamente após cada upagem ou alteração de atributo.
- **Critério de Aceitação:** Os valores dos modificadores correspondem às expectativas do sistema de RPG.

### RF-07: Rolar Atributos de Classe
- **Descrição:** Rola HP, Chakra e FP com base na fórmula específica da classe (ex: 15d5 para HP).
- **Flexibilidade:** Deve permitir diferentes fórmulas por classe.
- **Critério de Aceitação:** Os valores gerados estão dentro da faixa esperada para a classe.

## Módulo: Sistema de Combate

### RF-08: Iniciar Sessão de Combate
- **Comando:** `!startcombat <ficha_id>`
- **Descrição:** Cria uma cópia temporária dos atributos atuais do personagem para uma sessão de combate, com um TTL (Time-To-Live) de, por exemplo, 4 horas.
- **Critério de Aceitação:** Uma sessão de combate é criada com os atributos temporários e o TTL configurado.

### RF-09: Aplicar Dano
- **Comando:** `!dano <tipo> <valor>`
- **Tipos:** HP, Chakra, FP.
- **Descrição:** Aplica dano a um atributo específico do personagem na sessão de combate.
- **Validação:** Verifica se há uma sessão ativa e se o tipo e valor são válidos.
- **Alertas:** Alerta quando um atributo atinge zero.
- **Critério de Aceitação:** Os valores são decrementados corretamente e alertas são emitidos quando apropriado.

### RF-10: Aplicar Cura
- **Comando:** `!cura <tipo> <valor>`
- **Tipos:** HP, Chakra, FP.
- **Descrição:** Aplica cura a um atributo específico do personagem na sessão de combate.
- **Restrição:** Não pode exceder o valor máximo do atributo.
- **Critério de Aceitação:** Os valores são incrementados corretamente sem exceder o máximo.

### RF-11: Finalizar Sessão de Combate
- **Comando:** `!endcombat [--persist]`
- **Descrição:** Finaliza uma sessão de combate.
- **Opção `--persist`:** Se presente, aplica as mudanças temporárias ao personagem permanente.
- **Sem `--persist`:** Descarta todas as mudanças feitas durante a sessão.
- **Critério de Aceitação:** As mudanças são aplicadas ou descartadas conforme a opção, e a sessão é encerrada.

## Módulo: Relatórios e Estatísticas

### RF-12: Relatório de Progresso
- **Comando:** `!progresso <ficha_id>`
- **Descrição:** Exibe um histórico de upagem do personagem, incluindo níveis ganhos, pontos distribuídos e evolução dos atributos.
- **Critério de Aceitação:** Os dados refletem o histórico correto do personagem.

### RF-13: Estatísticas de Uso
- **Comando:** `!stats`
- **Descrição:** Exibe estatísticas gerais do bot, como número total de personagens, comandos mais usados, etc.
- **Critério de Aceitação:** Os dados são precisos e atualizados.