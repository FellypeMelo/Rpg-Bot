# Diagramas de Sequência

Este documento contém diagramas de sequência que ilustram o fluxo de interação para os principais casos de uso do bot RPG.

## UC-01: Criar Ficha de Personagem

```plantuml
@startuml
actor "Usuário Discord" as User
participant "Discord Bot (discord_bot.py)" as Bot
participant "CharacterCommands" as CharCmd
participant "CharacterService" as CharService
participant "MongoDBRepository" as MongoRepo
participant "ClassTemplate (Entidade)" as ClassTemplateEntity
participant "Character (Entidade)" as CharacterEntity
participant "ModifierCalculator" as ModifierCalc
participant "AttributeCalculator" as AttributeCalc

User -> Bot: !ficha criar "Nome" "Classe"
Bot -> CharCmd: create_character(context, name, class_name, alias)
CharCmd -> CharService: create_character(name, class_name, alias)
CharService -> ClassTemplateEntity: Obtém template da classe (ex: Warrior)
CharService -> CharacterEntity: Cria nova instância de Character
CharService -> CharacterEntity: character.calculate_modifiers()
CharacterEntity -> ModifierCalc: calculate_all_modifiers(attributes)
ModifierCalc --> CharacterEntity: modifiers
CharacterEntity --> CharService:
CharService -> CharacterEntity: character.roll_class_attributes(class_template)
CharacterEntity -> AttributeCalc: roll_class_attributes(class_template)
AttributeCalc -> DiceRoller: roll_dice(formula)
DiceRoller --> AttributeCalc: roll_result
AttributeCalc --> CharacterEntity: hp, chakra, fp
CharacterEntity --> CharService:
CharService -> MongoRepo: save_character(character)
MongoRepo -> Database: Insere documento
Database --> MongoRepo: ID do documento
MongoRepo --> CharService: character_id
CharService --> CharCmd: character
CharCmd -> Bot: Envia mensagem de sucesso com ID e ficha formatada
Bot --> User: Mensagem de sucesso e ficha
@enduml
```

## UC-05: Aplicar Upagem

```plantuml
@startuml
actor "Usuário Discord" as User
participant "Discord Bot (discord_bot.py)" as Bot
participant "LevelUpCommands" as LevelUpCmd
participant "LevelUpService" as LevelUpService
participant "MongoDBRepository" as MongoRepo
participant "Character (Entidade)" as CharacterEntity
participant "ClassTemplate (Entidade)" as ClassTemplateEntity
participant "ModifierCalculator" as ModifierCalc
participant "AttributeCalculator" as AttributeCalc

User -> Bot: !up <ID> <níveis> <pts_status> <pts_maestria> <pts_ph>
Bot -> LevelUpCmd: apply_level_up(context, character_id, levels, status_points, mastery_points, ph_points)
LevelUpCmd -> LevelUpService: apply_level_up(character_id, levels, status_points, mastery_points, ph_points)
LevelUpService -> MongoRepo: get_character(character_id)
MongoRepo --> LevelUpService: character
LevelUpService -> ClassTemplateEntity: Obtém template da classe
LevelUpService -> CharacterEntity: Aplica pontos e níveis
LevelUpService -> CharacterEntity: character.calculate_modifiers()
CharacterEntity -> ModifierCalc: calculate_all_modifiers(attributes)
ModifierCalc --> CharacterEntity: modifiers
CharacterEntity --> LevelUpService:
LevelUpService -> CharacterEntity: character.roll_class_attributes(class_template)
CharacterEntity -> AttributeCalc: roll_class_attributes(class_template)
AttributeCalc -> DiceRoller: roll_dice(formula)
DiceRoller --> AttributeCalc: roll_result
AttributeCalc --> CharacterEntity: hp, chakra, fp
CharacterEntity --> LevelUpService:
LevelUpService -> MongoRepo: update_character(character)
MongoRepo --> LevelUpService: sucesso/falha
LevelUpService --> LevelUpCmd: updated_character
LevelUpCmd -> Bot: Envia mensagem de sucesso com detalhes da upagem
Bot --> User: Mensagem de sucesso
@enduml
```

## UC-08: Iniciar Sessão de Combate

```plantuml
@startuml
actor "Usuário Discord" as User
participant "Discord Bot (discord_bot.py)" as Bot
participant "CombatCommands" as CombatCmd
participant "CombatService" as CombatService
participant "MongoDBRepository" as MongoRepo
participant "RedisRepository" as RedisRepo
participant "Character (Entidade)" as CharacterEntity
participant "CombatSession (Entidade)" as CombatSessionEntity

User -> Bot: !startcombat <ficha_id>
Bot -> CombatCmd: start_combat(context, character_id)
CombatCmd -> CombatService: start_combat_session(character_id, guild_id, channel_id, player_id)
CombatService -> MongoRepo: get_character(character_id)
MongoRepo --> CombatService: character
CombatService -> RedisRepo: get_all_combat_sessions()
RedisRepo --> CombatService: active_sessions
CombatService -> CombatSessionEntity: Cria nova instância de CombatSession (cópia temporária do personagem)
CombatService -> RedisRepo: save_combat_session(combat_session, ttl_seconds)
RedisRepo -> Cache: Armazena sessão com TTL
Cache --> RedisRepo: sucesso
RedisRepo --> CombatService: session_id
CombatService --> CombatCmd: combat_session
CombatCmd -> Bot: Envia mensagem de sucesso com ID da sessão
Bot --> User: Mensagem de sucesso
@enduml
```

## UC-09: Aplicar Dano

```plantuml
@startuml
actor "Usuário Discord" as User
participant "Discord Bot (discord_bot.py)" as Bot
participant "CombatCommands" as CombatCmd
participant "CombatService" as CombatService
participant "RedisRepository" as RedisRepo
participant "CombatSession (Entidade)" as CombatSessionEntity

User -> Bot: !dano <ID_DA_SESSAO> <tipo> <valor>
Bot -> CombatCmd: apply_damage_command(context, session_id, attribute_type, value)
CombatCmd -> CombatService: apply_damage(session_id, attribute_type, value)
CombatService -> RedisRepo: get_combat_session(session_id)
RedisRepo --> CombatService: combat_session
CombatService -> CombatSessionEntity: Aplica dano ao atributo temporário
CombatService -> RedisRepo: update_combat_session(combat_session)
RedisRepo -> Cache: Atualiza sessão
Cache --> RedisRepo: sucesso
RedisRepo --> CombatService:
CombatService --> CombatCmd: updated_session
CombatCmd -> Bot: Envia mensagem com novo valor do atributo
Bot --> User: Mensagem de atualização
@enduml
```

## UC-11: Finalizar Sessão de Combate

```plantuml
@startuml
actor "Usuário Discord" as User
participant "Discord Bot (discord_bot.py)" as Bot
participant "CombatCommands" as CombatCmd
participant "CombatService" as CombatService
participant "RedisRepository" as RedisRepo
participant "MongoDBRepository" as MongoRepo
participant "Character (Entidade)" as CharacterEntity
participant "CombatSession (Entidade)" as CombatSessionEntity

User -> Bot: !endcombat <ID_DA_SESSAO> [--persist]
Bot -> CombatCmd: end_combat_session_command(context, session_id, persist)
CombatCmd -> CombatService: end_combat_session(session_id, persist_changes)
CombatService -> RedisRepo: get_combat_session(session_id)
RedisRepo --> CombatService: combat_session
alt if persist_changes is True
  CombatService -> MongoRepo: get_character(combat_session.character_id)
  MongoRepo --> CombatService: character
  CombatService -> CharacterEntity: Aplica mudanças temporárias ao personagem permanente
  CombatService -> MongoRepo: update_character(character)
  MongoRepo --> CombatService: sucesso/falha
end
CombatService -> RedisRepo: delete_combat_session(session_id)
RedisRepo -> Cache: Remove sessão
Cache --> RedisRepo: sucesso
RedisRepo --> CombatService: sucesso/falha
CombatService --> CombatCmd: sucesso/falha
CombatCmd -> Bot: Envia mensagem de finalização
Bot --> User: Mensagem de finalização
@enduml