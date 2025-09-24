# 🎮 Bem-vindo ao RPG Bot v2.2!

Seu assistente definitivo para campanhas de RPG no Discord. Gerencie fichas, combates por turnos, transformações e muito mais!

## 🚀 Primeiros Passos (Copie e Cole!)

1.  **Crie seu personagem:**
    ```!ficha criar "Seu Nome" SuaClasse```
    *Exemplo:* `!ficha criar "Aragorn" Desgarrado`

2.  **Defina seu favorito (opcional, mas útil!):**
    ```!favorito "Seu Nome"```
    *Exemplo:* `!favorito "Aragorn"`

3.  **Veja sua ficha a qualquer momento:**
    ```!ficha ver "Seu Nome"```
    *Exemplo:* `!ficha ver "Aragorn"`

## ⚔️ Comandos Essenciais (Simples e Diretos)

| Comando | O que faz | Exemplo Fácil |
| :--- | :--- | :--- |
| `!ficha criar "Nome" Classe` | Cria um novo personagem. | `!ficha criar "Gandalf" Mago` |
| `!up "Nome" N` | Sobe N níveis. | `!up "Gandalf" 1` |
| `!pontos "Nome"` | Mostra seus pontos. | `!pontos "Gandalf"` |
| `!gastar status "Nome" atr qtd` | Gasta pontos de status. | `!gastar "Gandalf" int 5` |
| `!gastar ph "Nome" qtd "motivo"` | Gasta PH. | `!gastar "Gandalf" 1 "Bola de Fogo"` |
| `!favorito "Nome"` | Define favorito. | `!favorito "Gandalf"` |
| `!rodar atr [bonus]` | Rola 1d20 + mod. | `!rodar sab` ou `!rodar car 2` |

## ✨ Transformações (Poderes Especiais)

| Comando | O que faz | Exemplo Fácil |
| :--- | :--- | :--- |
| `!addtransformacao "Nome" "Poder"` | (Mestre) Adiciona um poder. | `!addtransformacao "Gandalf" "Modo Branco"` |
| `!edittransformacao "Nome" {"bonus": {"atributos": {"multiplicadores": {"forca": 2.0, "constituicao": 1.5}}}, "duracao_segundos": 600}` | (Mestre) Edita um poder. | `!edittransformacao "Modo Branco" {"bonus": {"atributos": {"multiplicadores": {"forca": 2.0}}}}` |
| `!transformar "Nome" "Poder"` | Ativa seu poder. | `!transformar "Gandalf" "Modo Branco"` |
| `!destransformar "Nome" "Poder"` | Desativa seu poder. | `!destransformar "Gandalf" "Modo Branco"` |

## 🎲 Combate por Turnos (Passo a Passo)

1.  **Mestre inicia:** `!startcombat`
2.  **Todos entram:** `!iniciativa "Gandalf" "Frodo" Orc+2`
3.  **Mestre começa:** `!comecar`
4.  **Jogador age (seu turno):** `!dano 10 Orc` ou `!cura 5`
5.  **Mestre avança:** `!proximo`
6.  **Mestre termina:** `!endcombat`

## ❓ Precisa de Ajuda?
- `!help` — Mostra todos os comandos.
- `!help rodar` — Explica um comando específico.

> **Dica Rápida:** Use `!favorito` e depois comandos como `!rodar for` sem precisar digitar o nome do personagem toda vez!