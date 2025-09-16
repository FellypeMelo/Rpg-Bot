# Diagrama de Implantação

Este diagrama de implantação ilustra a arquitetura de infraestrutura para o bot RPG, mostrando como os componentes são implantados em diferentes nós.

```plantuml
@startuml
node "Servidor Discord" as DiscordServer {
  component "Discord API" as DiscordAPI
}

node "Servidor de Aplicação (Python)" as ApplicationServer {
  component "RPG Discord Bot (discord_bot.py)" as BotApp
  component "Application Commands" as AppCommands
  component "Application Services" as AppServices
  component "Core Entities" as CoreEntities
  component "Calculators" as Calculators
  component "Utilities" as Utilities
}

node "Servidor de Banco de Dados (MongoDB)" as MongoDBServer {
  database "MongoDB Database" as MongoDB
}

node "Servidor de Cache (Redis)" as RedisServer {
  database "Redis Cache" as Redis
}

cloud "Serviços de Backup" as BackupServices {
  component "Daily Backup Script" as DailyBackup
  component "Restore Script" as RestoreScript
}

cloud "Serviços de Manutenção" as MaintenanceServices {
  component "Cleanup Sessions Script" as CleanupSessions
  component "Database Maintenance Script" as DBMaintenance
}

cloud "Serviços de Monitoramento" as MonitoringServices {
  component "Health Check Script" as HealthCheck
  component component "Logging System" as LoggingSystem
}

User --> DiscordServer : Interage
DiscordServer <--> BotApp : API do Discord

BotApp --> AppCommands : Usa
AppCommands --> AppServices : Usa
AppServices --> CoreEntities : Gerencia
AppServices --> Calculators : Usa
AppServices --> Utilities : Usa

AppServices <--> MongoDB : Persistência de Personagens
AppServices <--> Redis : Sessões de Combate

DailyBackup --> MongoDB : Backup de dados
DailyBackup --> Redis : Backup de dados
RestoreScript --> MongoDB : Restauração de dados
RestoreScript --> Redis : Restauração de dados

CleanupSessions --> Redis : Limpeza de sessões
DBMaintenance --> MongoDB : Manutenção de DB

HealthCheck --> DiscordAPI : Verifica Bot
HealthCheck --> MongoDB : Verifica DB
HealthCheck --> Redis : Verifica Cache

BotApp --> LoggingSystem : Envia logs
AppServices --> LoggingSystem : Envia logs
AppCommands --> LoggingSystem : Envia logs
Utilities --> LoggingSystem : Envia logs

@enduml