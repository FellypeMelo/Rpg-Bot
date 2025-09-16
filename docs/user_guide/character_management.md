# Gerenciamento de Personagens

Este guia detalha como usar os comandos de gerenciamento de personagens do bot RPG.

## 1. Criar um Personagem (`!ficha criar`)
Este comando permite que você crie uma nova ficha de personagem.

- **Sintaxe:** `!ficha criar "Nome do Personagem" <Classe> [--alias "Apelido"]`
- **Exemplo:**
  ```
  !ficha criar "Sir Galahad" Cavaleiro --alias "O Puro"
  ```
- **Detalhes:**
  - O `Nome do Personagem` é obrigatório e deve ser único. Use aspas duplas se o nome tiver espaços.
  - A `Classe` é obrigatória e define os atributos base, fórmulas de HP/Chakra/FP e bônus de upagem.
  - O `Apelido` é opcional e pode ser usado para se referir ao personagem de forma mais curta.

## 2. Visualizar a Ficha de um Personagem (`!ficha ver`)
Use este comando para exibir todos os detalhes de uma ficha de personagem.

- **Sintaxe:** `!ficha ver <ID_DO_PERSONAGEM_OU_NOME>`
- **Exemplo:**
  ```
  !ficha ver 123e4567-e89b-12d3-a456-426614174000
  !ficha ver "Sir Galahad"
  !ficha ver "O Puro"
  ```
- **Detalhes:**
  - Você pode usar o ID único do personagem ou o nome/apelido para visualizá-lo.
  - A resposta incluirá todos os atributos, modificadores, pontos de vida, maestrias e pontos disponíveis.

## 3. Atualizar um Personagem (`!ficha atualizar`)
Este comando permite modificar campos específicos da sua ficha.

- **Sintaxe:** `!ficha atualizar <ID_DO_PERSONAGEM> <campo> <valor>`
- **Campos Atualizáveis:**
  - `name`: O novo nome do personagem (string).
  - `alias`: O novo apelido do personagem (string).
  - `masteries`: Um dicionário JSON de maestrias e seus novos valores (ex: `'{"swords": 3, "archery": 1}'`).
- **Exemplos:**
  - **Atualizar o nome:**
    ```
    !ficha atualizar 123e4567-e89b-12d3-a456-426614174000 name "Galahad, O Cavaleiro"
    ```
  - **Atualizar o apelido:**
    ```
    !ficha atualizar 123e4567-e89b-12d3-a456-426614174000 alias "O Cavaleiro Puro"
    ```
  - **Atualizar maestrias:**
    ```
    !ficha atualizar 123e4567-e89b-12d3-a456-426614174000 masteries '{"swords": 4, "shields": 3}'
    ```
- **Detalhes:**
  - Certifique-se de que o `valor` para `masteries` seja um JSON válido.

## 4. Excluir um Personagem (`!ficha excluir`)
Este comando remove permanentemente uma ficha de personagem. Tenha cuidado, pois esta ação não pode ser desfeita.

- **Sintaxe:** `!ficha excluir <ID_DO_PERSONAGEM>`
- **Exemplo:**
  ```
  !ficha excluir 123e4567-e89b-12d3-a456-426614174000
  ```
- **Detalhes:**
  - Após usar o comando, o bot pedirá uma confirmação. Você deve responder `sim` para prosseguir com a exclusão.