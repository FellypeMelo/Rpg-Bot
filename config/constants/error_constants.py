# Error Messages
ERROR_MESSAGES = {
    "COMMAND_NOT_FOUND": "Comando não encontrado. Use `!ajuda` para ver os comandos disponíveis.",
    "MISSING_ARGUMENTS": "Argumentos faltando. Verifique `!ajuda {command_name}`.",
    "INVALID_ARGUMENT": "Argumento inválido. Verifique `!ajuda {command_name}`.",
    "NO_PERMISSION": "Você não tem permissão para usar este comando.",
    "BOT_OWNER_ONLY": "Este comando só pode ser usado pelo proprietário do bot.",
    "UNEXPECTED_ERROR": "Ocorreu um erro inesperado: {error_message}",

    "CHARACTER_NOT_FOUND": "Personagem com ID/nome/apelido '{identifier}' não encontrado.",
    "INVALID_CLASS_NAME": "Classe '{class_name}' não encontrada ou não suportada.",
    "INVALID_BASE_ATTRIBUTES": "Atributos base fornecidos são inválidos para esta classe.",
    "FIELD_NOT_UPDATABLE": "O campo '{field_name}' não pode ser atualizado diretamente.",
    "INVALID_MASTERY_FORMAT": "O valor para 'masteries' deve ser um objeto JSON (dicionário).",
    "INVALID_JSON_FORMAT": "Formato JSON inválido para '{field_name}'.",

    "LEVEL_UP_CHARACTER_NOT_FOUND": "Personagem com ID '{character_id}' não encontrado para upagem.",
    "LEVEL_UP_INVALID_CLASS": "Classe '{class_name}' não encontrada ou não suportada para upagem.",
    "LEVEL_UP_EXCEED_STATUS_POINTS": "Pontos de status gastos excedem os pontos disponíveis.",
    "LEVEL_UP_EXCEED_MASTERY_POINTS": "Pontos de maestria gastos excedem os pontos disponíveis.",
    "LEVEL_UP_EXCEED_PH_POINTS": "Pontos de PH gastos excedem os pontos disponíveis.",
    "LEVEL_UP_NEGATIVE_PH_POINTS": "Pontos de PH gastos não podem ser negativos.",
    "LEVEL_UP_INVALID_ATTRIBUTE": "Atributo '{attribute_name}' inválido.",
    "LEVEL_UP_INVALID_LEVELS": "O número de níveis a ganhar deve ser maior que zero.",

    "COMBAT_CHARACTER_NOT_FOUND": "Personagem com ID '{character_id}' não encontrado para iniciar combate.",
    "COMBAT_MAX_SESSIONS_REACHED": "Você já tem {max_sessions} sessões de combate ativas. Finalize uma para iniciar outra.",
    "COMBAT_SESSION_NOT_FOUND": "Sessão de combate com ID '{session_id}' não encontrada ou inativa.",
    "COMBAT_INVALID_ATTRIBUTE_TYPE": "Tipo de atributo '{attribute_type}' inválido. Use 'hp', 'chakra' ou 'fp'.",
    "COMBAT_DAMAGE_VALUE_POSITIVE": "Valor de dano deve ser positivo.",
    "COMBAT_HEALING_VALUE_POSITIVE": "Valor de cura deve ser positivo.",
    "COMBAT_PERSIST_CHARACTER_NOT_FOUND": "Personagem original com ID '{character_id}' não encontrado para persistir mudanças.",

    "DATABASE_CONNECTION_ERROR": "Falha ao conectar ao banco de dados: {error_message}",
    "REPOSITORY_ERROR": "Erro no repositório: {error_message}",
    "CACHE_ERROR": "Erro no cache: {error_message}",

    "FILE_NOT_FOUND": "Arquivo '{file_path}' não encontrado.",
    "PERMISSION_DENIED": "Permissão negada para acessar '{file_path}'.",
    "INVALID_FILE_FORMAT": "Formato de arquivo inválido para '{file_path}'.",
}