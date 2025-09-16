# Requisitos Não Funcionais (RNFs)

Este documento detalha os requisitos não funcionais para o bot Discord de gerenciamento de fichas de RPG.

## RNF-01: Performance
- **Tempo de Resposta do Comando:** Menos de 200ms para a maioria dos comandos.
- **Operações de Banco de Dados:** Menos de 100ms para operações CRUD básicas.
- **Métrica:** Testes de carga com 50 usuários simultâneos devem manter os tempos de resposta dentro dos limites especificados.

## RNF-02: Escalabilidade
- **Suporte a Personagens:** Deve suportar até 10.000 personagens sem degradação significativa de performance.
- **Crescimento Estimado:** O sistema deve ser capaz de lidar com um crescimento de aproximadamente 100 novos personagens por mês.

## RNF-03: Confiabilidade
- **Disponibilidade:** 99.5% de disponibilidade.
- **Tempo Máximo de Inatividade:** Não mais que 4 horas por mês.
- **Backup:** Backups diários automatizados de todos os dados críticos, com retenção de 7 dias.
- **Tempo de Recuperação (RTO):** Tempo máximo de 2 horas para restaurar o serviço em caso de falha.

## RNF-04: Segurança
- **Validação de Entrada:** Todas as entradas do usuário devem ser validadas para prevenir ataques de injeção (ex: NoSQL injection).
- **Rate Limiting:** Limite máximo de 10 comandos por minuto por usuário para prevenir spam e abuso.
- **Verificação de Permissões:** Comandos destrutivos (ex: exclusão de personagem) devem ter verificações de permissão adequadas para garantir que apenas usuários autorizados possam executá-los.

## RNF-05: Usabilidade
- **Mensagens de Erro:** Mensagens de erro claras, concisas e informativas para o usuário.
- **Ajuda Integrada:** Fornecer um comando de ajuda (`!ajuda`) que liste os comandos disponíveis e suas sintaxes.
- **Formatação Consistente:** As respostas do bot devem ter uma formatação consistente e fácil de ler no Discord.
- **Documentação Abrangente:** Fornecer documentação completa para usuários e desenvolvedores.