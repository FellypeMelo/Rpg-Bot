# Regras de Negócio (RNs)

Este documento descreve as regras de negócio que governam o comportamento do bot Discord de gerenciamento de fichas de RPG.

## RN-01: Sistema de Nivelamento
- **Pontos por Nível:** Para cada nível ganho, um personagem recebe 3 pontos de status, 2 pontos de maestria e 1 ponto de PH (Pontos de Habilidade).
- **PH Não Negativo:** O valor de PH de um personagem nunca pode ser negativo.
- **Pontos Acumulados:** Pontos de status, maestria e PH não utilizados são acumulados para futuras upagens.

## RN-02: Cálculo de Modificadores
- **Fórmula Padrão:** O modificador para cada atributo (Força, Destreza, Constituição, Inteligência, Sabedoria, Carisma) é calculado pela fórmula: `modificador = floor((Status / 3) - 1)`.
- **Arredondamento:** O arredondamento deve ser sempre para baixo (função `floor`).

## RN-03: Sistema de Combate
- **Alterações Temporárias:** Todas as alterações nos atributos de um personagem durante uma sessão de combate são temporárias e não afetam a ficha permanente, a menos que explicitamente persistidas.
- **Persistência Explícita:** As mudanças de combate só são persistidas na ficha permanente se o comando de finalização de combate for executado com a opção `--persist`.
- **HP Zero:** Se o HP de um personagem atingir zero durante o combate, o personagem é considerado incapacitado.
- **Chakra/FP Zero:** Se o Chakra ou FP de um personagem atingir zero durante o combate, o personagem não pode usar habilidades que dependam desses recursos.

## RN-04: Rolagem de Atributos
- **HP:** O HP inicial de um personagem é determinado pela fórmula de rolagem de dados específica da sua classe (exemplo: 15d5).
- **Chakra e FP:** Similarmente, o Chakra e o FP iniciais são determinados por fórmulas de rolagem de dados específicas da classe.
- **Variação por Classe:** As fórmulas de rolagem para HP, Chakra e FP podem variar significativamente entre as diferentes classes de personagens.

## RN-05: Gerenciamento de Sessões
- **Expiração de Sessão:** As sessões de combate expiram automaticamente após 4 horas de inatividade.
- **Máximo de Sessões por Usuário:** Um usuário pode ter no máximo 3 sessões de combate simultâneas ativas.
- **Limpeza Automática:** Sessões antigas e expiradas devem ser automaticamente limpas do sistema.

## RN-06: Políticas de Dados
- **Dados de Personagem:** Os dados de personagens são retidos indefinidamente, a menos que o personagem seja explicitamente excluído.
- **Dados de Combate:** Os dados de sessões de combate têm um TTL (Time-To-Live) de 24 horas no cache Redis.
- **Logs de Auditoria:** Os logs de auditoria são retidos por 30 dias.

## RN-07: Políticas de Segurança
- **Validação de Entradas:** Todas as entradas do usuário devem ser rigorosamente validadas para prevenir vulnerabilidades como injeção de NoSQL.
- **Rate Limiting:** Um mecanismo de rate limiting deve ser implementado para limitar o número de comandos que um usuário pode executar em um determinado período, prevenindo spam e ataques de negação de serviço.
- **Backups Diários:** Backups diários de todos os dados críticos devem ser realizados para garantir a recuperação em caso de perda de dados.