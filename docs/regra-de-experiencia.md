# Regra de experiência

Como o personagem ganha EXP ao derrotar um monstro. **A regra vive só no backend** (`backend/core/exp_rule.py`). O combate roda no cliente, mas o cliente não calcula EXP: ele apenas avisa quais monstros o herói abateu e se morreu, e o backend decide o valor e grava.

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
| Herói abate um monstro | o abate entra em `state.pending_kills`; logo em seguida o cliente o envia, o backend soma o EXP, recalcula o nível ([Progressão de level](progressao-de-level.md)) e grava. O log mostra "Charname gains N EXP" (e "level up to Level N", se subiu) com os valores devolvidos |
| Clica em **Leave** | só espera algum envio em andamento e reporta o que ainda faltar; a EXP já está salva |
| Herói **morre** | o cliente envia os abates com `defeated: true`; o backend soma o EXP, recalcula o nível e tira **20% da EXP acumulada no nível atual** (arredondado para baixo, contando o que ganhou na caçada). A perda nunca vem da EXP total, então **morrer não faz perder nível**. O log mostra "Charname loses N EXP" quando a resposta chega |

Exemplo: o herói no nível 1 começa com 50 de EXP, ganha 6 e morre: 56 − 11 = **45**. No nível 3 com 250 de EXP total (50 dentro do nível), morrer tira 10 (20% de 50): fica com 240 e continua no nível 3.

O salvamento é `POST /api/v1/characters/{id}/battle-result` (ver [Endpoints](endpoints-backend.md)), feito a cada abate (e na morte). Como a EXP é gravada na hora, fechar o app no meio da caçada **não perde** a EXP já ganha.

### O que o backend valida

O cliente não envia valores de EXP, então não dá para gravar um número arbitrário. Ele ainda pode mentir sobre **quais monstros abateu** (a batalha roda no cliente); o backend só confere que cada nome existe (404 se não) e limita a lista a 1000 abates.

## No código

- `backend/core/exp_rule.py`: `exp_percentage(hero_level, monster_level)` devolve a porcentagem; `exp_gain(hero_level, monster_level, base_exp)` devolve o EXP; `exp_after_death(exp)` aplica `DEATH_EXP_PENALTY` (20%).
- As faixas ficam nas listas `HERO_HIGHER_TIERS` e `HERO_LOWER_TIERS` (limite da diferença, porcentagem); a última faixa não tem limite. Para mudar a regra, edite só esse arquivo.
- `endpoints/characters.py`: `post_battle_result` recalcula o EXP de cada abate com o nível atual do personagem, soma, recalcula o nível, aplica a perda se `defeated` e grava. Devolve `{character, exp_gained, exp_lost}`.
- Frontend: quando o herói abate um monstro, `perform_attack` anota o nome em `state.pending_kills`. Só o herói ganha; abates feitos por monstros não geram EXP.
- `battle_page.settle` (chamada pelo `anim_loop` a cada quadro e pelo Leave) envia os abates pendentes (e a morte, uma vez: `state.defeat_reported`) com `CharacterService.send_battle_result`, atualiza o personagem em `session_state` e registra no log `LogEntry(kind="exp")`, `level_up` e `exp_loss` conforme a resposta. `state.settling` evita dois envios ao mesmo tempo.

## O que ainda falta

- Os `base_exp` atuais (Poring 6, Lunatic 8, Wilow 10) são valores provisórios.
