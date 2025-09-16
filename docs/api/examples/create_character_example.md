# Exemplo de Uso: Criar Personagem

Este exemplo demonstra como usar o comando `!ficha criar` para criar um novo personagem no bot RPG.

## Comando
`!ficha criar "Nome do Personagem" <Classe> [--alias "Apelido"]`

## Cenário
Vamos criar um personagem chamado "Elara" da classe "Mage" com o apelido "A Sábia".

## Passos
1. **Abra o Discord:** Certifique-se de estar em um servidor onde o bot RPG está ativo e você tem permissão para usar seus comandos.

2. **Digite o Comando:** No canal de texto, digite o seguinte comando:
   ```
   !ficha criar "Elara" Mage --alias "A Sábia"
   ```

3. **Resposta do Bot:** O bot processará o comando e responderá com uma mensagem de sucesso, incluindo o ID único do personagem e uma representação JSON da ficha criada.

   Exemplo de resposta do bot:
   ```
   Personagem 'Elara' da classe 'Mage' criado com sucesso! ID: `a1b2c3d4-e5f6-7890-1234-567890abcdef`
   ```
   (seguido por um bloco de código JSON com os detalhes da ficha)

   ```json
   {
     "id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
     "name": "Elara",
     "alias": "A Sábia",
     "class_name": "Mage",
     "level": 1,
     "experience": 0,
     "attributes": {
       "strength": 8,
       "dexterity": 10,
       "constitution": 10,
       "intelligence": 14,
       "wisdom": 12,
       "charisma": 6
     },
     "modifiers": {
       "strength": 1,
       "dexterity": 2,
       "constitution": 2,
       "intelligence": 3,
       "wisdom": 3,
       "charisma": 1
     },
     "hp": 30,
     "max_hp": 30,
     "chakra": 60,
     "max_chakra": 60,
     "fp": 15,
     "max_fp": 15,
     "masteries": {},
     "ph_points": 1,
     "status_points": 3,
     "mastery_points": 2,
     "inventory": [],
     "skills": [],
     "spells": [],
     "equipment": {},
     "created_at": "2025-09-14T18:00:00.000000",
     "updated_at": "2025-09-14T18:00:00.000000"
   }
   ```

## Observações
- O `ID` gerado é único para cada personagem e será necessário para outros comandos (como `!ficha ver` ou `!up`).
- Os `atributos`, `modificadores`, `hp`, `chakra` e `fp` são calculados automaticamente com base na `class_name` fornecida.
- Os `ph_points`, `status_points` e `mastery_points` iniciais são definidos pelas regras de negócio da classe.