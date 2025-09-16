# Guia de Início Rápido

Bem-vindo ao guia de início rápido do bot RPG! Este documento irá ajudá-lo a configurar e começar a usar o bot para gerenciar suas fichas de personagem no Discord.

## 1. Pré-requisitos
Antes de começar, certifique-se de ter o seguinte:
- Uma conta Discord.
- Permissões para adicionar bots ao seu servidor Discord (se você for o administrador do servidor).
- Python 3.11+ instalado em seu ambiente de desenvolvimento (se você for executar o bot localmente).
- Docker e Docker Compose (recomendado para fácil implantação de MongoDB e Redis).

## 2. Instalação e Configuração (para Desenvolvedores/Administradores)

### 2.1. Clonar o Repositório
Primeiro, clone o repositório do bot para sua máquina local:
```bash
git clone https://github.com/seu-usuario/rpg-bot.git
cd rpg-bot
```

### 2.2. Configurar Ambiente Virtual
Crie e ative um ambiente virtual Python:
```bash
python -m venv .venv
# No Windows
.\.venv\Scripts\activate
# No macOS/Linux
source .venv/bin/activate
```

### 2.3. Instalar Dependências
Instale as bibliotecas Python necessárias:
```bash
pip install -r requirements.txt
```

### 2.4. Configurar Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto e adicione as seguintes variáveis:
```
DISCORD_TOKEN=SEU_TOKEN_DO_BOT_DISCORD
MONGODB_CONNECTION_STRING=mongodb://localhost:27017/
MONGODB_DATABASE_NAME=rpg_bot_db
MONGODB_CHARACTER_COLLECTION=characters
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```
- **`DISCORD_TOKEN`**: Obtenha este token no [Portal do Desenvolvedor Discord](https://discord.com/developers/applications).
- **`MONGODB_CONNECTION_STRING`**: A string de conexão para o seu servidor MongoDB.
- **`REDIS_HOST`**, **`REDIS_PORT`**, **`REDIS_DB`**: Detalhes de conexão para o seu servidor Redis.

### 2.5. Executar o Bot
Para iniciar o bot, execute o seguinte comando:
```bash
python src/infrastructure/external/discord_bot.py
```
O bot deverá se conectar ao Discord e você verá uma mensagem no console indicando que ele está online.

## 3. Adicionar o Bot ao seu Servidor Discord
1. Vá para o [Portal do Desenvolvedor Discord](https://discord.com/developers/applications).
2. Selecione sua aplicação de bot.
3. Vá para a seção "OAuth2" -> "URL Generator".
4. Em "SCOPES", selecione `bot`.
5. Em "BOT PERMISSIONS", selecione as permissões necessárias (ex: `Send Messages`, `Read Message History`, `Manage Channels` se necessário para interações mais avançadas).
6. Copie o URL gerado e cole-o no seu navegador.
7. Selecione o servidor Discord onde você deseja adicionar o bot e autorize.

## 4. Primeiros Comandos
Agora que o bot está online e no seu servidor, você pode começar a usá-lo!

- **`!ficha criar "Nome do Personagem" Classe`**: Crie sua primeira ficha.
- **`!ficha ver <ID_DO_PERSONAGEM>`**: Visualize a ficha que você acabou de criar.
- **`!ajuda`**: Obtenha uma lista de todos os comandos disponíveis.

Para mais detalhes sobre os comandos, consulte a [Referência de Comandos](commands_reference.md).