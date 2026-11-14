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

## Perda e salvamento

| Evento | O que acontece com a EXP |
|---|---|
| Herói abate um monstro | ganha o EXP da regra acima; aparece no Battle Log ("Charname gains N EXP") |
| Clica em **Leave** | sai com a EXP ganha na caçada: o total é salvo no personagem |
| Herói **morre** | perde **20%** da EXP atual (arredondado para baixo), contando o que ganhou na caçada; aparece no log ("Charname loses N EXP") e o total é salvo na hora |

Exemplo: o herói começa com 50 de EXP, ganha 6 e morre: 56 − 11 = **45**.

O salvamento é `PATCH /api/v1/characters/{id}/exp` (ver [Endpoints](endpoints-backend.md)), feito uma vez por caçada e só se a EXP mudou. Fechar o app no meio da caçada, sem Leave nem morte, **não salva** a EXP ganha.

## No código

- `exp_percentage(hero_level, monster_level)` devolve a porcentagem; `exp_gain(hero_level, monster_level, base_exp)` devolve o EXP.
- As faixas ficam nas listas `HERO_HIGHER_TIERS` e `HERO_LOWER_TIERS` (limite da diferença, porcentagem); a última faixa não tem limite. Para mudar a regra, edite essas listas.
- Quando o herói abate um monstro, `perform_attack` soma o ganho em `state.exp_gained` e em `hero["exp"]` e registra `LogEntry(kind="exp")`. Só o herói ganha; abates feitos por monstros não geram EXP.
- `exp_after_death(exp)` aplica `DEATH_EXP_PENALTY` (20%); é chamada por `BattleState.check_battle_end`, que registra `LogEntry(kind="exp_loss")`.
- `battle_page.save_exp` envia `hero["exp"]` ao backend (`CharacterService.update_exp`) uma única vez (`state.exp_saved`): no Leave e quando a batalha termina em derrota. Depois atualiza o personagem em `session_state`.

## O que ainda falta

- **Subir de nível**: não existe tabela de progressão. A barra de EXP usa `MAX_EXP_DEFAULT = 100` (ver [Personagens](personagens.md)) e fica cheia quando a EXP passa disso.
- Os `base_exp` atuais (Poring 6, Lunatic 8, Wilow 10) são valores provisórios.
