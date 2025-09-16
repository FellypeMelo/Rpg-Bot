# Guia de Combate

Este guia explica como usar os comandos do sistema de combate do bot RPG para gerenciar suas sessões de combate.

## 1. Iniciar uma Sessão de Combate (`!startcombat`)
Para começar um combate, você precisa iniciar uma sessão para o seu personagem. Isso cria uma cópia temporária da sua ficha, permitindo que você aplique dano e cura sem afetar permanentemente seu personagem até que você decida persistir as mudanças.

- **Sintaxe:** `!startcombat <ID_DO_PERSONAGEM>`
- **Exemplo:**
  ```
  !startcombat 123e4567-e89b-12d3-a456-426614174000
  ```
- **Detalhes:**
  - O bot responderá com um `ID da Sessão` único. Guarde este ID, pois ele será usado para todos os outros comandos de combate.
  - Você pode ter um número limitado de sessões de combate ativas simultaneamente (padrão: 3).
  - As sessões expiram após 4 horas de inatividade.

## 2. Aplicar Dano (`!dano`)
Use este comando para aplicar dano aos atributos de HP, Chakra ou FP do seu personagem na sessão de combate.

- **Sintaxe:** `!dano <ID_DA_SESSAO> <tipo_atributo> <valor>`
- **Tipos de Atributo:**
  - `hp`: Pontos de Vida
  - `chakra`: Pontos de Chakra
  - `fp`: Pontos de Foco
- **Exemplos:**
  - **Aplicar 20 de dano ao HP:**
    ```
    !dano abcdef12-3456-7890-abcd-ef1234567890 hp 20
    ```
  - **Aplicar 10 de dano ao Chakra:**
    ```
    !dano abcdef12-3456-7890-abcd-ef1234567890 chakra 10
    ```
- **Detalhes:**
  - Se o HP chegar a zero, o bot alertará que o personagem está incapacitado.
  - Se Chakra ou FP chegarem a zero, o bot alertará que o personagem não pode usar habilidades que dependam desses recursos.

## 3. Aplicar Cura (`!cura`)
Use este comando para restaurar HP, Chakra ou FP do seu personagem na sessão de combate.

- **Sintaxe:** `!cura <ID_DA_SESSAO> <tipo_atributo> <valor>`
- **Tipos de Atributo:**
  - `hp`: Pontos de Vida
  - `chakra`: Pontos de Chakra
  - `fp`: Pontos de Foco
- **Exemplos:**
  - **Curar 15 de HP:**
    ```
    !cura abcdef12-3456-7890-abcd-ef1234567890 hp 15
    ```
  - **Curar 5 de FP:**
    ```
    !cura abcdef12-3456-7890-abcd-ef1234567890 fp 5
    ```
- **Detalhes:**
  - A cura não pode exceder o valor máximo do atributo.

## 4. Finalizar uma Sessão de Combate (`!endcombat`)
Quando o combate terminar, você pode finalizar a sessão. Você tem a opção de salvar as mudanças na ficha permanente do seu personagem ou descartá-las.

- **Sintaxe:** `!endcombat <ID_DA_SESSAO> [--persist]`
- **Opções:**
  - Sem `--persist`: Todas as mudanças feitas durante a sessão de combate serão descartadas. A ficha permanente do seu personagem permanecerá inalterada.
  - Com `--persist`: As mudanças nos atributos (HP, Chakra, FP) feitas durante a sessão serão aplicadas à ficha permanente do seu personagem.
- **Exemplos:**
  - **Finalizar e descartar mudanças:**
    ```
    !endcombat abcdef12-3456-7890-abcd-ef1234567890
    ```
  - **Finalizar e salvar mudanças:**
    ```
    !endcombat abcdef12-3456-7890-abcd-ef1234567890 --persist
    ```
- **Detalhes:**
  - Após a finalização, a sessão de combate temporária será removida.