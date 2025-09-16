# Diagrama de Componentes

Este diagrama de componentes ilustra a estrutura de alto nível do bot RPG, mostrando os principais módulos e suas interações.

```plantuml
@startuml
skinparam componentStyle rectangle

package "RPG Bot" {
  [Discord Bot Adapter] as DiscordAdapter
  [Character Commands] as CharCmd
  [LevelUp Commands] as LevelUpCmd
  [Combat Commands] as CombatCmd
  [Report Commands] as ReportCmd

  package "Application Services" {
    [Character Service] as CharService
    [LevelUp Service] as LevelUpService
    [Combat Service] as CombatService
    [Report Service] as ReportService
  }

  package "Core Entities" {
    [Character] as CharacterEntity
    [Combat Session] as CombatSessionEntity
    [Class Template] as ClassTemplateEntity
  }

  package "Calculators" {
    [Modifier Calculator] as ModifierCalc
    [Dice Roller] as DiceRoller
    [Attribute Calculator] as AttributeCalc
  }

  package "Infrastructure" {
    [MongoDB Repository] as MongoRepo
    [Redis Repository] as RedisRepo
  }

  package "Utilities" {
    [Input Validators] as InputValidators
    [Application Exceptions] as AppExceptions
    [Infrastructure Exceptions] as InfraExceptions
    [Logger] as Logger
    [Audit Logger] as AuditLogger
    [Formatters] as Formatters
    [Dice Parser] as DiceParser
  }
}

actor "Discord User" as User
actor "Discord API" as DiscordAPI

User --> DiscordAdapter : Interage via comandos
DiscordAdapter --> DiscordAPI : Comunica com a API do Discord

DiscordAdapter --> CharCmd
DiscordAdapter --> LevelUpCmd
DiscordAdapter --> CombatCmd
DiscordAdapter --> ReportCmd

CharCmd .> CharService : Usa
LevelUpCmd .> LevelUpService : Usa
CombatCmd .> CombatService : Usa
ReportCmd .> ReportService : Usa

CharService .> CharacterEntity : Gerencia
LevelUpService .> CharacterEntity : Atualiza
CombatService .> CharacterEntity : Atualiza
CombatService .> CombatSessionEntity : Gerencia
CharService .> ClassTemplateEntity : Usa

CharService .> ModifierCalc : Usa
CharService .> AttributeCalc : Usa
LevelUpService .> ModifierCalc : Usa
LevelUpService .> AttributeCalc : Usa
CombatService .> DiceRoller : Usa

CharService .> MongoRepo : Persiste/Recupera
LevelUpService .> MongoRepo : Persiste/Recupera
ReportService .> MongoRepo : Recupera
CombatService .> MongoRepo : Persiste/Recupera
CombatService .> RedisRepo : Persiste/Recupera

CharCmd .> InputValidators : Valida
LevelUpCmd .> InputValidators : Valida
CombatCmd .> InputValidators : Valida

CharCmd .> AppExceptions : Lança
LevelUpCmd .> AppExceptions : Lança
CombatCmd .> AppExceptions : Lança
CharService .> AppExceptions : Lança
LevelUpService .> AppExceptions : Lança
CombatService .> AppExceptions : Lança

MongoRepo .> InfraExceptions : Lança
RedisRepo .> InfraExceptions : Lança

Logger .> DiscordAdapter : Loga eventos
AuditLogger .> CharService : Loga ações
AuditLogger .> LevelUpService : Loga ações
AuditLogger .> CombatService : Loga ações

Formatters .> CharCmd : Formata saída
Formatters .> LevelUpCmd : Formata saída
Formatters .> CombatCmd : Formata saída
Formatters .> ReportCmd : Formata saída

DiceParser .> DiceRoller : Analisa notação

@enduml