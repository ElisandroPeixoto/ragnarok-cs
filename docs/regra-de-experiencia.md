# Regra de experiência

Como o personagem ganha EXP ao derrotar um monstro. A regra está em `frontend/services/battle_exp.py` e é aplicada em `perform_attack` (`services/battle_actions.py`) no momento em que o herói abate um monstro.

## Dados envolvidos

| Dado | Onde fica | Observação |
|---|---|---|
| `base_exp` | `MonsterModel.base_exp` (Integer, padrão 0) | EXP base do monstro, definido por monstro em `MONSTERS` (`backend/seed_data.py`) |
| `level` do monstro | `MonsterModel.level` | |
| `level` do personagem | `CharacterModel.level` | vai para a batalha em `hero_unit` |

`base_exp` e `level` chegam ao frontend em cada unidade do `spawn_pool` (`monster_unit`) e na lista `monsters` da resposta do mapa.

## A regra

A diferença de nível é **nível do personagem − nível do monstro**. Até 5 níveis de diferença, para mais ou para menos, o ganho é 100% do `base_exp`.

| Situação | Diferença de nível | Ganho (% do `base_exp`) |
|---|---|---|
| Nível igual ou diferença de até 5 (qualquer lado) | 0 a 5 | **100%** |
| Personagem **maior** | 6 a 10 | **90%** |
| Personagem **maior** | 11 a 30 | **50%** |
| Personagem **maior** | mais de 30 | **10%** |
| Personagem **menor** | 6 a 10 | **110%** |
| Personagem **menor** | 11 a 30 | **120%** |
| Personagem **menor** | mais de 30 | **40%** |

O último caso (personagem mais de 30 níveis abaixo) cai para 40% de propósito: evita que um personagem de nível baixo seja fortalecido de graça por um aliado de nível alto em monstros muito fortes.

### Arredondamento

`ganho = base_exp × porcentagem ÷ 100`, **arredondado para baixo** (divisão inteira). Com `base_exp` pequeno, 10% pode dar 0.

### Exemplos

| Personagem | Monstro | `base_exp` | Diferença | Ganho |
|---|---|---|---|---|
| Lv 1 | Lv 1 | 10 | 0 | 10 |
| Lv 8 | Lv 3 | 10 | +5 | 10 |
| Lv 20 | Lv 12 | 100 | +8 | 90 |
| Lv 50 | Lv 30 | 100 | +20 | 50 |
| Lv 70 | Lv 10 | 100 | +60 | 10 |
| Lv 5 | Lv 13 | 100 | −8 | 110 |
| Lv 5 | Lv 25 | 100 | −20 | 120 |
| Lv 5 | Lv 50 | 100 | −45 | 40 |

## No código

- `exp_percentage(hero_level, monster_level)` devolve a porcentagem; `exp_gain(hero_level, monster_level, base_exp)` devolve o EXP.
- As faixas ficam nas listas `HERO_HIGHER_TIERS` e `HERO_LOWER_TIERS` (limite da diferença, porcentagem); a última faixa não tem limite. Para mudar a regra, edite essas listas.
- Quando o herói abate um monstro, `perform_attack` soma o ganho em `state.exp_gained` e registra uma entrada `LogEntry(kind="exp")` no Battle Log: "Charname gains N EXP". Só o herói ganha; abates feitos por monstros não geram EXP.

## O que ainda falta

- **Persistir o EXP**: `state.exp_gained` vale só durante a caçada; nenhuma rota grava o EXP no personagem.
- **Subir de nível**: não existe tabela de progressão (a barra de EXP usa `MAX_EXP_DEFAULT = 100`, ver [Personagens](personagens.md)).
- Os `base_exp` atuais (Poring 6, Lunatic 8, Wilow 10) são valores provisórios.
