# RPG Bot Discord

## Sobre o Projeto
Bot de RPG para Discord com comandos de criação de personagens, combate, progressão e relatórios. Utiliza arquitetura modular com MongoDB/Redis para persistência.

## Requisitos
- Python 3.11+
- Dependências: `pip install -r requirements.txt`
- Variáveis de ambiente:
  ```env
  DISCORD_TOKEN=seu_token_aqui
  MONGODB_URI=mongodb://localhost:27017
  REDIS_URI=redis://localhost:6379
  ```

## Configuração
Ajuste os settings em `config/settings/development_settings.py` para:
- Tempo de sessão
- Configurações de banco de dados
- Parâmetros de logging

## Como Rodar
```bash
# Instalar dependências
pip install -r requirements.txt

# Instalar projeto em modo desenvolvedor
pip install -e .

# Iniciar o bot
cd src/infrastructure/external
python discord_bot.py
```

## Comandos Disponíveis
Veja referência completa em [`docs/api/commands_reference.md`](docs/api/commands_reference.md). Exemplos:
- `!criar_personagem` - Cria novo personagem
- `!atacar` - Inicia ataque em combate
- `!subir_nivel` - Atualiza nível de personagem

## Estrutura do Projeto
```bash
src/
├── application/       # Comandos Discord e validações
├── core/              # Lógica de domínio (atributos, dados, combate)
├── infrastructure/    # Implementações externas (Discord, MongoDB, Redis)
└── utils/             # Funções auxiliares e exceções

docs/                  # Documentação técnica e de usuário
config/                # Configurações e constantes
scripts/               # Manutenção e backup
tests/                 # Testes unitários e integração
```

## Contribuição
1. Crie branch feature
2. Execute testes com `pytest tests/`
3. Mantenha PEP8 e docstrings
4. Submeta pull request com descrição detalhada