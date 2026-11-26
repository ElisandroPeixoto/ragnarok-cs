# Regra de experiência

Como o personagem ganha EXP ao derrotar um monstro. **A regra vive só no backend** (`backend/core/exp_rule.py`). O combate roda no cliente, mas o cliente não calcula EXP: ele apenas avisa como a caçada terminou (vitória ou derrota) e, na vitória, quais monstros o herói matou. O backend decide o valor e grava.

## Dados envolvidos

| Dado | Onde fica | Observação |
|---|---|---|
| `base_exp` | `MonsterModel.base_exp` (Integer, padrão 0) | EXP base do monstro, definido por monstro em `MONSTERS` (`backend/seed_data.py`) |
| `level` do monstro | `MonsterModel.level` | |
| `level` do personagem | `CharacterModel.level` | vai para a batalha em `hero_unit` |

O frontend não recebe `base_exp` para calcular nada: ele mostra no Battle Log o `exp_gained` que o backend devolve. A lista `monsters` da resposta do mapa traz `level` e `base_exp`, só informativos.

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
| Herói mata um monstro | o log mostra "Charname gains N EXP" (o `exp_reward` do monstro), mas **nada é gravado**: a EXP fica pendente (`state.exp_pending`) |
| **Vitória** (todos os monstros mortos) | a batalha sai sozinha; o backend soma a EXP de **todos** os monstros, recalcula o nível ([Progressão de level](progressao-de-level.md)) e grava |
| **Derrota** (o herói morre) | a EXP dos monstros mortos **não é paga**; o backend tira **20% da EXP acumulada no nível atual** (arredondado para baixo). A perda nunca vem da EXP total, então **morrer não faz perder nível** |
| Clica em **Leave** | não perde nada e **não recebe** a EXP dos monstros que já matou: nenhum envio é feito |

Exemplo: o herói no nível 1 com 50 de EXP vence uma caçada de 3 monstros que valem 6 + 8 + 10: fica com 74. Se morrer com 50, perde 10 (20%) e fica com 40, sem receber nada pelos monstros que matou. No nível 3 com 250 de EXP total (50 dentro do nível), morrer tira 10: fica com 240 e continua no nível 3.

O salvamento é `POST /api/v1/characters/{id}/battle-result` (ver [Endpoints](endpoints-backend.md)), **uma única vez, ao fim da batalha**. Fechar o app no meio da caçada não grava nada (como o Leave).

### O que o backend valida

O cliente não envia valores de EXP, então não dá para gravar um número arbitrário. Ele ainda pode mentir sobre **quais monstros matou** (a batalha roda no cliente); o backend só confere que a vitória traz de 1 a 6 nomes (422 se não) e que cada nome existe (404 se não). Numa derrota os nomes são ignorados.

## No código

- `backend/core/exp_rule.py`: `exp_percentage(hero_level, monster_level)` devolve a porcentagem; `exp_gain(hero_level, monster_level, base_exp)` devolve o EXP; `exp_after_death(exp)` aplica `DEATH_EXP_PENALTY` (20%).
- As faixas ficam nas listas `HERO_HIGHER_TIERS` e `HERO_LOWER_TIERS` (limite da diferença, porcentagem); a última faixa não tem limite. Para mudar a regra, edite só esse arquivo.
- `endpoints/battles.py`: `monster_unit` preenche `exp_reward` com `exp_gain` para o nível do herói (só para o log). O nível não muda durante a caçada, então o valor do log é o mesmo que o backend vai pagar.
- `endpoints/characters.py`: `post_battle_result`. Vitória: valida 1 a 6 nomes, soma o EXP de cada um com o nível atual do personagem, recalcula o nível e grava. Derrota: ignora os nomes e aplica a perda de 20% do progresso do nível. Devolve `{character, exp_gained, exp_lost}`.
- Frontend: quando o herói mata um monstro, `perform_attack` anota o nome em `state.kills`, soma `exp_reward` em `state.exp_pending` e registra `LogEntry(kind="exp")`. Só o herói ganha; monstros não geram EXP.
- `battle_page.finish_battle` envia `CharacterService.send_battle_result(id, victory, kills)` (uma vez, quando surge o vencedor), atualiza o personagem em `session_state` e guarda o relatório para o pop up de resultado.

## O que ainda falta

- Os `base_exp` atuais (Poring 6, Lunatic 8, Wilow 10) são valores provisórios.
